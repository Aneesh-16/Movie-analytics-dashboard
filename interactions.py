"""Shared user-interaction API (ratings, likes, watchlist, recommendation events).
Private data rules: a normal user sees only their own rows; editors may read everyone's."""
import logging
from typing import Literal

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

import analytics as an
from auth import Principal, current_user
from database import get_session, movies_df
from models import Interaction, Movie
from schemas import InteractionIn, RecommendationFeedback

log = logging.getLogger("movie_analytics")
router = APIRouter(prefix="/api")
SLOTS = {"rating": "rating", "like": "reaction", "dislike": "reaction", "watchlist": "watchlist"}


def as_dict(i: Interaction) -> dict:
    return an.clean({"id": i.id, "user_id": i.user_id, "movie_id": i.movie_id, "interaction_type": i.interaction_type,
                     "rating": i.rating, "active": i.active, "metadata": i.meta,
                     "created_at": i.created_at.isoformat() if i.created_at else None,
                     "updated_at": i.updated_at.isoformat() if i.updated_at else None})


def authorize_user_id(who: Principal, user_id: str) -> None:
    if who.role != "editor" and who.username != user_id:
        raise HTTPException(403, "You may only access your own interaction history")


def _commit(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Duplicate interaction")
    except SQLAlchemyError:
        session.rollback()
        log.exception("Interaction write failed")
        raise HTTPException(503, "Database write failed; nothing was saved")


def save_interaction(session: Session, user_id: str, body: InteractionIn) -> tuple[Interaction, bool]:
    if session.get(Movie, body.movie_id) is None:
        raise HTTPException(404, f"Movie with id {body.movie_id} not found")
    t = body.interaction_type
    stored = "watchlist" if t.startswith("watchlist") else t
    active, slot = t != "watchlist_remove", SLOTS.get(stored)
    existing = session.scalar(select(Interaction).where(
        Interaction.user_id == user_id, Interaction.movie_id == body.movie_id, Interaction.slot == slot)) if slot else None
    if t == "watchlist_remove" and existing is None:
        raise HTTPException(404, "Movie is not on this user's watchlist")
    if existing:       # state-like types are updated in place: never duplicated
        existing.interaction_type, existing.rating, existing.active = stored, body.rating, active
        if body.metadata is not None:
            existing.meta = body.metadata
        row, created = existing, False
    else:
        row = Interaction(user_id=user_id, movie_id=body.movie_id, interaction_type=stored, slot=slot,
                          rating=body.rating, active=active, meta=body.metadata)
        session.add(row)
        created = True
    _commit(session)
    session.refresh(row)
    return row, created


@router.post("/interactions", status_code=201, tags=["interactions"])
def create_interaction(body: InteractionIn, response: Response, who: Principal = Depends(current_user),
                       session: Session = Depends(get_session)):
    """Record an interaction for the logged-in user. 201 = new row, 200 = existing rating/reaction/watchlist row updated.
    rating: needs `rating` 1-10. like/dislike replace each other. watchlist_add / watchlist_remove toggle `active`.
    recommendation_impression / _click / _feedback are appended as events."""
    row, created = save_interaction(session, who.username, body)
    if not created:
        response.status_code = 200
    return as_dict(row)


@router.post("/recommendation-feedback", status_code=201, tags=["interactions"])
def recommendation_feedback(body: RecommendationFeedback, who: Principal = Depends(current_user),
                            session: Session = Depends(get_session)):
    """Store feedback on a recommendation made by the partner application."""
    meta = {"feedback": body.feedback, **{k: v for k, v in body.model_dump(exclude={"movie_id", "feedback"}).items() if v is not None}}
    row, _ = save_interaction(session, who.username, InteractionIn(
        movie_id=body.movie_id, interaction_type="recommendation_feedback", metadata=meta))
    return as_dict(row)


@router.get("/interactions", tags=["interactions"])
def list_interactions(movie_id: int | None = None, interaction_type: str | None = None, user_id: str | None = None,
                      offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200),
                      who: Principal = Depends(current_user), session: Session = Depends(get_session)):
    """Your own interactions (editors can see everyone's and filter by user_id)."""
    if user_id:
        authorize_user_id(who, user_id)
    q = select(Interaction)
    if who.role != "editor":
        q = q.where(Interaction.user_id == who.username)
    elif user_id:
        q = q.where(Interaction.user_id == user_id)
    if movie_id:
        q = q.where(Interaction.movie_id == movie_id)
    if interaction_type:
        q = q.where(Interaction.interaction_type == interaction_type)
    total = session.scalar(select(func.count()).select_from(q.subquery()))
    rows = session.scalars(q.order_by(Interaction.updated_at.desc()).offset(offset).limit(limit)).all()
    return {"total": total, "offset": offset, "limit": limit, "items": [as_dict(r) for r in rows]}


@router.delete("/interactions/{interaction_id}", tags=["interactions"])
def delete_interaction(interaction_id: int, who: Principal = Depends(current_user), session: Session = Depends(get_session)):
    """Undo your own rating/like/event. (To leave a watchlist use watchlist_remove.)"""
    row = session.get(Interaction, interaction_id)
    if row is None:
        raise HTTPException(404, "Interaction not found")
    authorize_user_id(who, row.user_id)
    session.delete(row)
    _commit(session)
    return {"deleted": interaction_id}


def _user_rows(session, user_id, where):
    movies = {m.id: m for m in session.scalars(select(Movie).join(Interaction, Interaction.movie_id == Movie.id)
                                              .where(Interaction.user_id == user_id, where))}
    rows = session.scalars(select(Interaction).where(Interaction.user_id == user_id, where)
                           .order_by(Interaction.updated_at.desc())).all()
    return rows, movies


@router.get("/users/{user_id}/watchlist", tags=["interactions"])
def watchlist(user_id: str, who: Principal = Depends(current_user), session: Session = Depends(get_session)):
    authorize_user_id(who, user_id)
    rows, movies = _user_rows(session, user_id, (Interaction.interaction_type == "watchlist") & Interaction.active.is_(True))
    return {"user_id": user_id, "count": len(rows), "items": [
        {"movie_id": r.movie_id, "title": movies[r.movie_id].title, "year": movies[r.movie_id].year,
         "poster_path": movies[r.movie_id].poster_path, "added_at": as_dict(r)["updated_at"]} for r in rows]}


@router.get("/users/{user_id}/ratings", tags=["interactions"])
def user_ratings(user_id: str, who: Principal = Depends(current_user), session: Session = Depends(get_session)):
    authorize_user_id(who, user_id)
    rows, movies = _user_rows(session, user_id, Interaction.interaction_type == "rating")
    return {"user_id": user_id, "count": len(rows), "items": [
        {"movie_id": r.movie_id, "title": movies[r.movie_id].title, "personal_rating": r.rating,
         "tmdb_rating": movies[r.movie_id].vote_average, "rated_at": as_dict(r)["updated_at"]} for r in rows]}


@router.get("/interactions/summary", tags=["interactions"])
def interactions_summary(session: Session = Depends(get_session)):
    """Public aggregate statistics computed from the interactions table (no user ids exposed)."""
    rows = session.execute(select(Interaction.user_id, Interaction.movie_id, Interaction.interaction_type,
                                  Interaction.rating, Interaction.active, Interaction.meta, Interaction.created_at)).all()
    inter = pd.DataFrame([tuple(r) for r in rows], columns=["user_id", "movie_id", "interaction_type", "rating",
                                                           "active", "meta", "created_at"])
    return an.interaction_summary(inter, movies_df(session))
