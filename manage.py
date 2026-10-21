"""Management commands (explicit, never run automatically):
   python manage.py init-db                  create tables (safe to repeat)
   python manage.py import-csv [--overwrite] import the two CSV files into the database
   python manage.py create-editor NAME       create/reset an editor account (password prompted)
   python manage.py enrich-posters [--limit N] [--retry-missing]   fetch poster paths from TMDB (needs TMDB_READ_TOKEN or TMDB_API_KEY)
   python manage.py list-editors
"""
import argparse
import getpass
import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from datetime import date

import pandas as pd
from sqlalchemy import inspect, insert, select, text

from config import CREDITS_CSV, MOVIES_CSV
from data_loader import load_dataset
from database import SessionLocal, engine, invalidate_cache
from models import Base, Editor, Movie, utcnow

log = logging.getLogger("movie_analytics")


NEW_MOVIE_COLUMNS = {"poster_path": "VARCHAR(200)", "poster_checked_at": "TIMESTAMP"}   # added after v2


def ensure_columns(eng=engine) -> list[str]:
    """Tiny migration: add columns introduced after v2 to an existing movies table. Never drops or changes data."""
    added = []
    existing = {c["name"] for c in inspect(eng).get_columns("movies")} if inspect(eng).has_table("movies") else None
    if existing is None:
        return added
    with eng.begin() as conn:
        for name, ddl in NEW_MOVIE_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE movies ADD COLUMN {name} {ddl}"))
                added.append(name)
    return added


def init_db() -> None:
    ensure_columns()                       # upgrade an existing v2 table first
    Base.metadata.create_all(engine)       # then create any missing tables; never drops anything


def _nz(v):
    """NaN / NA -> None so the database stores NULL."""
    return None if v is None or (not isinstance(v, (list, str)) and pd.isna(v)) else v


def _row(r: dict) -> dict:
    rd = _nz(r["release_date"])
    return {"id": int(r["id"]), "title": r["title"], "original_title": _nz(r["original_title"]),
            "overview": _nz(r["overview"]), "tagline": _nz(r["tagline"]), "status": _nz(r["status"]),
            "release_date": date.fromisoformat(rd) if rd else None,
            "year": None if _nz(r["year"]) is None else int(r["year"]),
            "vote_average": _nz(r["vote_average"]), "vote_count": int(r["vote_count"]),
            "popularity": _nz(r["popularity"]),
            "budget": None if _nz(r["budget"]) is None else int(r["budget"]),
            "revenue": None if _nz(r["revenue"]) is None else int(r["revenue"]),
            "runtime": _nz(r["runtime"]), "original_language": _nz(r["original_language"]),
            "genres": r["genres_list"], "keywords": r["keywords_list"],
            "production_companies": r["companies_list"], "production_countries": r["countries_list"],
            "director": _nz(r["director"]), "cast_members": r["cast_full"], "crew_members": r["crew_key"]}


def import_csv(session, movies_path=MOVIES_CSV, credits_path=CREDITS_CSV, overwrite=False) -> dict:
    """Insert movies whose TMDB id is not in the database yet.
    Re-running never creates duplicates and never touches existing (possibly edited) rows,
    unless overwrite=True (explicitly resets those rows to the CSV values)."""
    rows = [_row(r) for r in load_dataset(movies_path, credits_path).to_dict("records")]
    existing = set(session.scalars(select(Movie.id)))
    new = [r for r in rows if r["id"] not in existing]
    for i in range(0, len(new), 500):
        session.execute(insert(Movie), new[i:i + 500])
    overwritten = 0
    if overwrite:
        for r in rows:
            if r["id"] in existing:
                session.merge(Movie(**r))
                overwritten += 1
    session.commit()
    invalidate_cache()
    return {"csv_rows": len(rows), "inserted": len(new), "already_present": len(rows) - len(new),
            "overwritten": overwritten}


class TmdbTransient(Exception):
    """Temporary problem (network, rate limit, bad key): the movie is NOT marked as checked."""


def tmdb_fetch_poster(movie_id: int) -> str | None:
    """Ask the official TMDB API for this exact movie id. The key stays on the server/CLI - never in the browser."""
    token, key = os.environ.get("TMDB_READ_TOKEN"), os.environ.get("TMDB_API_KEY")
    if not (token or key):
        raise TmdbTransient("Set TMDB_READ_TOKEN or TMDB_API_KEY first")
    req = urllib.request.Request(f"https://api.themoviedb.org/3/movie/{movie_id}" + ("" if token else f"?api_key={key}"),
                                 headers={"Authorization": f"Bearer {token}"} if token else {})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.load(resp).get("poster_path")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None                    # TMDB does not know this id: remember that, do not retry
        raise TmdbTransient(f"TMDB returned HTTP {exc.code}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise TmdbTransient(str(exc))


def enrich_posters(session, fetch=tmdb_fetch_poster, limit=None, retry_missing=False, delay=0.03) -> dict:
    """Fill movies.poster_path. Matching is by TMDB id (no title guessing, so no look-alike mismatches).
    poster_checked_at caches the attempt, so each movie is asked about only once (unless --retry-missing)."""
    q = select(Movie).where(Movie.poster_path.is_(None) if retry_missing else Movie.poster_checked_at.is_(None))
    stats = {"checked": 0, "found": 0, "no_poster": 0, "errors": 0}
    for movie in session.scalars(q.order_by(Movie.popularity.desc())).all()[:limit]:
        try:
            path = fetch(movie.id)
        except TmdbTransient as exc:
            stats["errors"] += 1
            log.warning("Poster lookup skipped for %s: %s", movie.id, exc)
            if stats["errors"] >= 5:
                break                      # something systemic (key/network): stop early
            continue
        movie.poster_path, movie.poster_checked_at = path, utcnow()
        stats["checked"] += 1
        stats["found" if path else "no_poster"] += 1
        if stats["checked"] % 50 == 0:
            session.commit()
        time.sleep(delay)
    session.commit()
    invalidate_cache()
    return stats


def create_editor(session, username: str, password: str) -> str:
    from auth import hash_password
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,40}", username):
        raise ValueError("Username must be 3-40 characters: letters, digits, . _ -")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    editor = session.scalar(select(Editor).where(Editor.username == username))
    if editor:
        editor.password_hash = hash_password(password)
        action = "password updated"
    else:
        session.add(Editor(username=username, password_hash=hash_password(password)))
        action = "created"
    session.commit()
    return action


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db")
    imp = sub.add_parser("import-csv")
    imp.add_argument("--overwrite", action="store_true", help="DESTRUCTIVE: reset existing rows to CSV values")
    ce = sub.add_parser("create-editor")
    ce.add_argument("username")
    sub.add_parser("list-editors")
    ep = sub.add_parser("enrich-posters")
    ep.add_argument("--limit", type=int)
    ep.add_argument("--retry-missing", action="store_true")
    args = p.parse_args()
    print("Database:", engine.url.render_as_string(hide_password=True))
    init_db()
    with SessionLocal() as session:
        if args.cmd == "import-csv":
            if args.overwrite and input("This overwrites edited movies. Type YES to continue: ") != "YES":
                return
            print(import_csv(session, overwrite=args.overwrite))
        elif args.cmd == "create-editor":
            pw = os.environ.get("EDITOR_PASSWORD") or getpass.getpass("Password (min 8 chars): ")
            print(f"Editor '{args.username}':", create_editor(session, args.username, pw))
        elif args.cmd == "enrich-posters":
            print(enrich_posters(session, limit=args.limit, retry_missing=args.retry_missing))
        elif args.cmd == "list-editors":
            print([e for e in session.scalars(select(Editor.username))])
        elif args.cmd == "init-db":
            print("Tables ready.")


if __name__ == "__main__":
    main()
