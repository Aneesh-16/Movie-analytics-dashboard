"""REST API: thin route layer. Reads use a DB-derived snapshot; writes go straight to the database."""
import json
import logging
from typing import Literal

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

import analytics as an
from auth import Principal, current_editor, current_user, hash_password, make_token, verify_password
from config import DEFAULT_MIN_VOTES, MAX_LIMIT, TOKEN_TTL_SECONDS
from database import db_summary, get_session, invalidate_cache, movie_to_dict, movies_df
from models import AppUser, Editor, Interaction, Movie
from schemas import LoginRequest, MovieCreate, MovieUpdate, RegisterRequest

log = logging.getLogger("movie_analytics")
router = APIRouter(prefix="/api")
Sort = Literal["rating", "popularity", "revenue", "votes", "year", "title", "budget"]
Order = Literal["asc", "desc"]
_DUMMY_HASH = hash_password("timing-equaliser")


def get_df(session: Session = Depends(get_session)) -> pd.DataFrame:
    try:
        df = movies_df(session)
    except SQLAlchemyError:
        log.exception("Database error while reading movies")
        raise HTTPException(503, "Database unavailable")
    if df.empty:
        raise HTTPException(503, "No movies in the database yet. Run: python manage.py import-csv")
    return df


def check_years(year_from, year_to):
    if year_from is not None and year_to is not None and year_from > year_to:
        raise HTTPException(status_code=400, detail="year_from must not be greater than year_to")


@router.get("/health", tags=["system"])
def health(session: Session = Depends(get_session)):
    """Status, database connectivity, whether the dataset was imported, and the movie count."""
    try:
        n = db_summary(session)["movies"]
        return {"status": "ok", "database": "connected", "dataset_imported": n > 0, "movies": n}
    except SQLAlchemyError:
        log.exception("Health check: database unreachable")
        return {"status": "degraded", "database": "unavailable", "dataset_imported": False, "movies": 0}


# ---------- authentication ----------
@router.post("/users/register", status_code=201, tags=["auth"])
def register(body: RegisterRequest, session: Session = Depends(get_session)):
    """Create a normal user account (can record interactions, cannot edit the catalogue)."""
    taken = session.scalar(select(Editor.id).where(Editor.username == body.username)) or \
        session.scalar(select(AppUser.id).where(AppUser.username == body.username))
    if taken:
        raise HTTPException(409, "Username already taken")
    session.add(AppUser(username=body.username, password_hash=hash_password(body.password)))
    _commit(session)
    return {"username": body.username, "role": "user"}


@router.post("/auth/login", tags=["auth"])
def login(body: LoginRequest, session: Session = Depends(get_session)):
    """Works for editors and registered users; the token carries the role."""
    account, role = session.scalar(select(Editor).where(Editor.username == body.username)), "editor"
    if account is None:
        account, role = session.scalar(select(AppUser).where(AppUser.username == body.username)), "user"
    ok = verify_password(body.password, account.password_hash if account else _DUMMY_HASH)
    if not (account and ok):
        raise HTTPException(401, "Incorrect username or password")
    return {"token": make_token(account.username, role), "token_type": "bearer",
            "expires_in": TOKEN_TTL_SECONDS, "username": account.username, "role": role}


@router.get("/auth/me", tags=["auth"])
def me(user: Principal = Depends(current_user)):
    return {"username": user.username, "role": user.role}


# ---------- analytics (read-only, public). start/end = release-year period filter ----------
def period_df(start: int | None = Query(None, ge=1800, le=2100), end: int | None = Query(None, ge=1800, le=2100),
              df: pd.DataFrame = Depends(get_df)) -> pd.DataFrame:
    check_years(start, end)
    return an.in_period(df, start, end)


@router.get("/analytics/summary", tags=["analytics"])
def summary(start: int | None = Query(None, ge=1800, le=2100), end: int | None = Query(None, ge=1800, le=2100),
            df=Depends(get_df), session: Session = Depends(get_session)):
    """KPIs for the optional period. `catalogue_total` is always the whole catalogue."""
    check_years(start, end)
    out = an.summary(an.in_period(df, start, end))
    out["catalogue_total"] = len(df)
    out["period"] = {"start": start, "end": end}
    out["year_min"], out["year_max"] = an.clean(df["year"].min()), an.clean(df["year"].max())
    latest = session.scalar(select(func.max(Movie.updated_at)))
    out["last_updated"] = latest.isoformat() if hasattr(latest, "isoformat") else (str(latest) if latest else None)
    return out


@router.get("/analytics/genres", tags=["analytics"])
def genres(df=Depends(period_df)):
    return {"note": "A movie with several genres is counted in each of them, so genre counts add up to more than the number of movies.",
            "genres": an.genre_stats(df)}


@router.get("/analytics/years", tags=["analytics"])
def years(start: int | None = Query(None, ge=1800, le=2100), end: int | None = Query(None, ge=1800, le=2100),
          df=Depends(get_df)):
    check_years(start, end)
    return {"years": an.year_stats(df, start, end)}


@router.get("/analytics/ratings", tags=["analytics"])
def ratings(df=Depends(period_df)):
    return an.rating_stats(df)


@router.get("/analytics/financials", tags=["analytics"])
def financials(df=Depends(period_df)):
    return an.financial_stats(df)


@router.get("/analytics/languages", tags=["analytics"])
def languages(df=Depends(period_df)):
    return {"languages": an.language_stats(df)}


@router.get("/analytics/production", tags=["analytics"])
def production(df=Depends(period_df)):
    return an.production_stats(df)


@router.get("/analytics/compare", tags=["analytics"])
def compare(ids: str = Query(..., description="2-4 comma separated TMDB ids, e.g. 155,19995"),
            session: Session = Depends(get_session)):
    try:
        wanted = list(dict.fromkeys(int(x) for x in ids.split(",") if x.strip()))
    except ValueError:
        raise HTTPException(422, "ids must be comma separated integers")
    if not 2 <= len(wanted) <= 4:
        raise HTTPException(422, "Provide between 2 and 4 distinct movie ids")
    rows = {m.id: m for m in session.scalars(select(Movie).where(Movie.id.in_(wanted)))}
    missing = [i for i in wanted if i not in rows]
    if missing:
        raise HTTPException(404, f"Movie ids not found: {missing}")
    movies = [movie_to_dict(rows[i]) for i in wanted]
    return {"movies": movies, "highlights": an.compare_highlights(movies)}


def _list(df, q, genre, year_from, year_to, min_rating, min_votes, sort, order, offset, limit, language):
    check_years(year_from, year_to)
    frame = an.filter_movies(df, q, genre, year_from, year_to, min_rating, min_votes, sort, order, language)
    return an.paginate(frame, offset, limit)


@router.get("/movies", tags=["movies"])
def movies(q: str | None = None, genre: str | None = None, language: str | None = None, year_from: int | None = None,
           year_to: int | None = None, min_rating: float | None = Query(None, ge=0, le=10),
           min_votes: int | None = Query(None, ge=0), sort: Sort = "popularity", order: Order = "desc",
           offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=MAX_LIMIT), df=Depends(get_df)):
    return _list(df, q, genre, year_from, year_to, min_rating, min_votes, sort, order, offset, limit, language)


@router.get("/movies/search", tags=["movies"])
def search(q: str | None = None, genre: str | None = None, language: str | None = None, year_from: int | None = None,
           year_to: int | None = None, min_rating: float | None = Query(None, ge=0, le=10),
           min_votes: int | None = Query(None, ge=0), sort: Sort = "popularity", order: Order = "desc",
           offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=MAX_LIMIT), df=Depends(get_df)):
    """Same filters as /api/movies; `q` is a case-insensitive title substring."""
    return _list(df, q, genre, year_from, year_to, min_rating, min_votes, sort, order, offset, limit, language)


@router.get("/movies/top-rated", tags=["movies"])
def top_rated(min_votes: int = Query(DEFAULT_MIN_VOTES, ge=0), genre: str | None = None,
              year_from: int | None = None, year_to: int | None = None,
              offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=MAX_LIMIT), df=Depends(get_df)):
    check_years(year_from, year_to)
    frame = an.top_rated(df, min_votes, genre=genre, year_from=year_from, year_to=year_to)
    return an.paginate(frame, offset, limit)


@router.get("/movies/popular", tags=["movies"])
def popular(genre: str | None = None, offset: int = Query(0, ge=0),
            limit: int = Query(20, ge=1, le=MAX_LIMIT), df=Depends(get_df)):
    return an.paginate(an.filter_movies(df, genre=genre, sort="popularity"), offset, limit)


@router.get("/movies/{movie_id}", tags=["movies"])
def movie(movie_id: int, session: Session = Depends(get_session)):
    """Always read straight from the database (never from a cache)."""
    m = session.get(Movie, movie_id)
    if m is None:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    return movie_to_dict(m)


def _commit(session: Session):
    try:
        session.commit()                 # the write is durable before we answer
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Movie id already exists")
    except SQLAlchemyError:
        session.rollback()
        log.exception("Database write failed")
        raise HTTPException(503, "Database write failed; nothing was saved")
    invalidate_cache()


@router.post("/movies", status_code=201, tags=["movies (editors)"])
def create_movie(body: MovieCreate, editor: Editor = Depends(current_editor), session: Session = Depends(get_session)):
    """Create a new movie. Requires an editor token. The id must not already exist."""
    if session.get(Movie, body.id) is not None:
        raise HTTPException(409, f"Movie with id {body.id} already exists")
    data = body.model_dump()
    data["overview"] = data["overview"] or None
    m = Movie(**data, year=body.release_date.year if body.release_date else None, vote_count=0,
              keywords=[], production_companies=[], production_countries=[], cast_members=[], crew_members=[],
              last_edited_by=editor.username)
    session.add(m)
    _commit(session)
    return movie_to_dict(m)


@router.patch("/movies/{movie_id}", tags=["movies (editors)"])
def update_movie(movie_id: int, body: MovieUpdate, editor: Editor = Depends(current_editor),
                 session: Session = Depends(get_session)):
    """Update only the supplied fields. Requires an editor token. Returns the saved record."""
    changes = body.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(400, "No fields supplied")
    m = session.get(Movie, movie_id)
    if m is None:
        raise HTTPException(404, f"Movie with id {movie_id} not found")
    if "overview" in changes:
        changes["overview"] = changes["overview"] or None
    if "release_date" in changes:
        m.year = changes["release_date"].year if changes["release_date"] else None
    for field, value in changes.items():
        setattr(m, field, value)
    m.last_edited_by = editor.username
    _commit(session)
    session.refresh(m)
    return movie_to_dict(m)


# ---------- CSV export of the CURRENT database contents ----------
def _json(v):
    return json.dumps(v, ensure_ascii=False)


@router.get("/export/movies.csv", tags=["export (editors)"])
def export_movies(editor: Editor = Depends(current_editor), session: Session = Depends(get_session)):
    """Fresh CSV generated from the database (includes all edits). List fields are JSON text."""
    rows = session.scalars(select(Movie).order_by(Movie.id)).all()
    cols = ["id", "title", "original_title", "overview", "tagline", "status", "release_date", "vote_average",
            "vote_count", "popularity", "budget", "revenue", "runtime", "original_language", "genres", "keywords",
            "production_companies", "production_countries", "director", "poster_path", "created_at", "updated_at", "last_edited_by"]
    df = pd.DataFrame([{c: getattr(m, c) for c in cols} for m in rows], columns=cols)
    for c in ("budget", "revenue"):
        df[c] = pd.to_numeric(df[c]).astype("Int64")          # unknown stays blank; genuine 0 stays 0
    for c in ("genres", "keywords", "production_companies", "production_countries"):
        df[c] = df[c].map(_json)
    return Response(df.to_csv(index=False), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="movies_export.csv"'})


@router.get("/export/credits.csv", tags=["export (editors)"])
def export_credits(editor: Editor = Depends(current_editor), session: Session = Depends(get_session)):
    """movie_id,title,cast,crew - cast = top 20 {name, character}; crew = key crew {name, job, department} (JSON text)."""
    rows = session.scalars(select(Movie).order_by(Movie.id)).all()
    df = pd.DataFrame([{"movie_id": m.id, "title": m.title, "cast": _json(m.cast_members or []),
                        "crew": _json(m.crew_members or [])} for m in rows], columns=["movie_id", "title", "cast", "crew"])
    return Response(df.to_csv(index=False), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="credits_export.csv"'})


# ---------- data quality (editors) ----------
@router.get("/data/quality", tags=["data management (editors)"])
def data_quality(editor: Principal = Depends(current_editor), df=Depends(get_df)):
    """Coverage of optional fields and the most recent catalogue edits."""
    edited = df[df["last_edited_by"].notna()].sort_values("updated_at", ascending=False).head(10)
    return an.clean({
        "total": len(df), "with_poster": int(df["poster_path"].notna().sum()),
        "missing_budget": int(df["budget"].isna().sum()), "missing_revenue": int(df["revenue"].isna().sum()),
        "missing_runtime": int(df["runtime"].isna().sum()), "unrated": int(df["vote_average"].isna().sum()),
        "missing_overview": int(df["overview"].isna().sum()), "no_release_date": int(df["year"].isna().sum()),
        "edited_by_editors": int(df["last_edited_by"].notna().sum()),
        "recent_edits": [{"id": int(r["id"]), "title": r["title"], "last_edited_by": r["last_edited_by"],
                          "updated_at": r["updated_at"].isoformat() if hasattr(r["updated_at"], "isoformat") else str(r["updated_at"])}
                         for _, r in edited.iterrows()]})
