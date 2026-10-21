"""Database engine/session, plus a DB-derived analytics snapshot that refreshes whenever the data changes."""
import threading

import pandas as pd
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from analytics import clean
from config import DATABASE_URL
from models import Movie

engine = create_engine(DATABASE_URL, pool_pre_ping=True,
                       connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    """FastAPI dependency: one session per request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# --- analytics snapshot -------------------------------------------------------------------------
# The database is the only source of truth. For speed, analytics/search use a DataFrame built FROM the
# database. Before each use we run one cheap query (row count + latest updated_at); if either changed
# (an edit by anyone, or an import) the snapshot is rebuilt. So edits are never stale.
_cache: dict = {"sig": None, "df": None}
_lock = threading.Lock()
_COLS = ["id", "title", "overview", "release_date", "year", "vote_average", "vote_count", "popularity",
         "budget", "revenue", "runtime", "original_language", "genres", "keywords",
         "production_companies", "production_countries", "director", "cast_members", "poster_path", "updated_at",
         "last_edited_by"]


def invalidate_cache() -> None:
    _cache["sig"] = None


def _build_df(session: Session) -> pd.DataFrame:
    rows = session.execute(select(*[getattr(Movie, c) for c in _COLS])).all()
    df = pd.DataFrame([tuple(r) for r in rows], columns=_COLS)
    for col in ("year", "vote_average", "popularity", "budget", "revenue", "runtime"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)
    df["release_date"] = df["release_date"].map(lambda d: d.isoformat() if d else None)
    df["genres_list"] = df["genres"].map(lambda v: v or [])
    df["keywords_list"] = df["keywords"].map(lambda v: v or [])
    df["companies_list"] = df["production_companies"].map(lambda v: v or [])
    df["countries_list"] = df["production_countries"].map(lambda v: v or [])
    df["cast_list"] = df["cast_members"].map(lambda v: [p["name"] for p in (v or [])][:8])
    return df.drop(columns=["genres", "keywords", "production_companies", "production_countries", "cast_members"])


def movies_df(session: Session) -> pd.DataFrame:
    count, latest = session.execute(select(func.count(Movie.id), func.max(Movie.updated_at))).one()
    sig = (count, str(latest))
    with _lock:
        if _cache["sig"] != sig:
            _cache.update(df=_build_df(session), sig=sig)
        return _cache["df"]


def db_summary(session: Session) -> dict:
    """Used by /api/health: proves the connection works and shows how many movies exist."""
    return {"movies": session.scalar(select(func.count(Movie.id)))}


def movie_to_dict(m: Movie) -> dict:
    """Full movie record as returned by GET/POST/PATCH /api/movies/{id}."""
    d = {"id": m.id, "title": m.title, "year": m.year, "genres": m.genres or [],
         "rating": m.vote_average, "votes": m.vote_count, "popularity": m.popularity,
         "revenue": m.revenue, "budget": m.budget, "language": m.original_language,
         "vote_average": m.vote_average, "vote_count": m.vote_count,
         "release_date": m.release_date.isoformat() if m.release_date else None,
         "runtime": m.runtime, "overview": m.overview or None, "tagline": m.tagline or None,
         "status": m.status, "director": m.director, "poster_path": m.poster_path,
         "cast": [p["name"] for p in (m.cast_members or [])][:8], "crew": m.crew_members or [],
         "production_companies": m.production_companies or [], "production_countries": m.production_countries or [],
         "keywords": m.keywords or [], "updated_at": m.updated_at.isoformat() if m.updated_at else None,
         "last_edited_by": m.last_edited_by}
    if m.revenue and m.budget:
        d["estimated_profit"] = m.revenue - m.budget      # simplified, not audited profit
    return clean(d)
