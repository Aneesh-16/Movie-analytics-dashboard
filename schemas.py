"""Request validation (Pydantic). Only the fields below can be written; everything else is rejected."""
import json
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

Genre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]


class MovieFields(BaseModel):
    """Editable fields. extra='forbid' means id, vote_count, director, cast ... cannot be changed (HTTP 422)."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(None, min_length=1, max_length=300)
    overview: str | None = Field(None, max_length=5000)
    genres: list[Genre] | None = Field(None, max_length=20)
    release_date: date | None = None
    vote_average: float | None = Field(None, ge=0, le=10, allow_inf_nan=False)
    popularity: float | None = Field(None, ge=0, le=1_000_000, allow_inf_nan=False)
    budget: int | None = Field(None, ge=0, le=100_000_000_000)
    revenue: int | None = Field(None, ge=0, le=100_000_000_000)
    runtime: float | None = Field(None, ge=0, le=1000, allow_inf_nan=False)
    original_language: str | None = Field(None, pattern=r"^[a-z]{2,3}$")

    @field_validator("release_date")
    @classmethod
    def sane_date(cls, v):
        if v is not None and not (1870 <= v.year <= 2100):
            raise ValueError("release_date year must be between 1870 and 2100")
        return v


class MovieUpdate(MovieFields):
    """PATCH body: send only the fields to change. An explicit null clears optional fields (marks them unknown)."""

    @model_validator(mode="after")
    def required_not_null(self):
        for name in ("title", "genres", "popularity", "original_language"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class MovieCreate(MovieFields):
    id: int = Field(ge=1, le=2_147_483_647, description="TMDB movie id (must be new)")
    title: str = Field(min_length=1, max_length=300)
    genres: list[Genre] = Field(default_factory=list, max_length=20)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=1, max_length=200)


class RegisterRequest(BaseModel):
    username: str = Field(pattern=r"^[A-Za-z0-9_.-]{3,40}$")
    password: str = Field(min_length=8, max_length=200)


InteractionType = Literal["rating", "like", "dislike", "watchlist_add", "watchlist_remove",
                          "recommendation_impression", "recommendation_click", "recommendation_feedback"]


class InteractionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    movie_id: int = Field(ge=1)
    interaction_type: InteractionType
    rating: float | None = Field(None, ge=1, le=10, allow_inf_nan=False, description="personal rating 1-10")
    metadata: dict | None = None

    @model_validator(mode="after")
    def check(self):
        if (self.interaction_type == "rating") != (self.rating is not None):
            raise ValueError("rating is required for, and only allowed with, interaction_type 'rating'")
        if self.metadata is not None and len(json.dumps(self.metadata)) > 2000:
            raise ValueError("metadata is too large (max 2000 characters)")
        return self


class RecommendationFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid")
    movie_id: int = Field(ge=1)
    feedback: Literal["relevant", "not_relevant"]
    source_movie_id: int | None = Field(None, ge=1, description="movie the recommendation was based on")
    algorithm: str | None = Field(None, max_length=60)
    comment: str | None = Field(None, max_length=500)
