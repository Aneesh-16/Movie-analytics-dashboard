"""Database tables (SQLAlchemy). JSON columns become JSONB on PostgreSQL."""
from datetime import date, datetime, timezone

from sqlalchemy import (JSON, BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

JsonType = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Movie(Base):
    """One row per movie. `id` is the TMDB movie id and is the shared key for both applications.
    NULL means 'unknown' (e.g. budget 0 in TMDB); a stored 0 is a genuine zero."""
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    title: Mapped[str] = mapped_column(String(300), index=True)
    original_title: Mapped[str | None] = mapped_column(String(300))
    overview: Mapped[str | None] = mapped_column(Text)
    tagline: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(50))
    release_date: Mapped[date | None] = mapped_column(Date)
    year: Mapped[int | None] = mapped_column(Integer, index=True)
    vote_average: Mapped[float | None] = mapped_column(Float, index=True)
    vote_count: Mapped[int] = mapped_column(Integer, default=0)
    popularity: Mapped[float | None] = mapped_column(Float, index=True)
    budget: Mapped[int | None] = mapped_column(BigInteger)
    revenue: Mapped[int | None] = mapped_column(BigInteger)
    runtime: Mapped[float | None] = mapped_column(Float)
    original_language: Mapped[str | None] = mapped_column(String(10), index=True)
    genres: Mapped[list] = mapped_column(JsonType, default=list)                  # ["Action", ...]
    keywords: Mapped[list] = mapped_column(JsonType, default=list)
    production_companies: Mapped[list] = mapped_column(JsonType, default=list)
    production_countries: Mapped[list] = mapped_column(JsonType, default=list)
    director: Mapped[str | None] = mapped_column(String(200))
    cast_members: Mapped[list] = mapped_column(JsonType, default=list)            # top 20: {name, character}
    crew_members: Mapped[list] = mapped_column(JsonType, default=list)            # key crew: {name, job, department}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    last_edited_by: Mapped[str | None] = mapped_column(String(60))
    poster_path: Mapped[str | None] = mapped_column(String(200))          # TMDB poster path, e.g. /abc.jpg
    poster_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # enrichment cache marker


class Editor(Base):
    """Accounts allowed to call POST/PATCH. Only a salted scrypt hash of the password is stored."""
    __tablename__ = "editors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AppUser(Base):
    """Registered (non-editor) users. Their username is the `user_id` stored on interactions."""
    __tablename__ = "app_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Interaction(Base):
    """User activity, kept separate from TMDB's own vote_average.
    State-like types share a `slot`, so one user has at most ONE row per movie for each slot:
      rating -> 'rating', like/dislike -> 'reaction', watchlist -> 'watchlist' (active true/false).
    Event types (recommendation_impression/click/feedback) have slot NULL and are appended."""
    __tablename__ = "interactions"
    __table_args__ = (UniqueConstraint("user_id", "movie_id", "slot", name="uq_user_movie_slot"),
                      Index("ix_interactions_movie_type", "movie_id", "interaction_type"))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(60), index=True)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id"), index=True)
    interaction_type: Mapped[str] = mapped_column(String(40))
    slot: Mapped[str | None] = mapped_column(String(20))
    rating: Mapped[float | None] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    meta: Mapped[dict | None] = mapped_column("metadata", JsonType)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
