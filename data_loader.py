"""CSV reading layer: validate, parse, clean and join the two TMDB CSV files.
Used only by the explicit import (manage.py import-csv). The live data is read from the database."""
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from config import CREDITS_CSV, MOVIES_CSV

log = logging.getLogger("movie_analytics")

MOVIE_COLUMNS = {"id", "title", "genres", "release_date", "popularity", "vote_average",
                 "vote_count", "budget", "revenue", "runtime", "original_language",
                 "overview", "keywords", "production_companies", "production_countries"}
CREDIT_COLUMNS = {"movie_id", "cast", "crew"}
KEY_JOBS = {"Director", "Writer", "Screenplay", "Producer", "Executive Producer",
            "Original Music Composer", "Director of Photography", "Editor"}


class DatasetError(Exception):
    """Raised when the dataset is missing or has an unexpected structure."""


def parse_json_list(value) -> list:
    """Safely parse a JSON-like string into a list. Malformed/missing -> []."""
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        log.warning("Malformed JSON skipped: %.60s", value)
        return []
    return data if isinstance(data, list) else []


def extract_names(value, key: str = "name", limit: int | None = None) -> list[str]:
    names = [i[key] for i in parse_json_list(value) if isinstance(i, dict) and i.get(key)]
    return names[:limit] if limit else names


def extract_director(crew) -> str | None:
    for person in parse_json_list(crew):
        if isinstance(person, dict) and person.get("job") == "Director" and person.get("name"):
            return person["name"]
    return None


def _read_csv(path: Path, required: set[str]) -> pd.DataFrame:
    if not Path(path).exists():
        raise DatasetError(f"Dataset file not found: {path}. Place the TMDB CSV files in the 'data' folder "
                           "(tmdb_5000_movies.csv and tmdb_5000_credits.csv).")
    df = pd.read_csv(path)
    missing = required - set(df.columns)
    if missing:
        raise DatasetError(f"{Path(path).name} is missing required columns: {sorted(missing)}")
    return df


def load_dataset(movies_path=MOVIES_CSV, credits_path=CREDITS_CSV) -> pd.DataFrame:
    """Load both CSVs, join on movies.id == credits.movie_id and return a cleaned DataFrame."""
    movies = _read_csv(movies_path, MOVIE_COLUMNS)
    credits = _read_csv(credits_path, CREDIT_COLUMNS)

    # Deliberate duplicate handling: keep first record per movie id.
    movies = movies.drop_duplicates("id")
    credits = credits.drop_duplicates("movie_id")
    df = movies.merge(credits[["movie_id", "cast", "crew"]], left_on="id", right_on="movie_id",
                      how="left").drop(columns="movie_id")

    # Numeric cleaning: 0 in budget/revenue/runtime means "unknown" in TMDB, so use NaN, not 0.
    for col in ("budget", "revenue", "runtime"):
        df[col] = pd.to_numeric(df[col], errors="coerce").replace(0, np.nan)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
    df.loc[df["vote_count"] == 0, "vote_average"] = np.nan   # unrated movies are not "0 stars"
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce")

    # Dates
    dates = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = dates.dt.year
    df["release_date"] = dates.dt.strftime("%Y-%m-%d")

    # Nested JSON fields
    df["title"] = df["title"].fillna("Untitled").astype(str)
    df["genres_list"] = df["genres"].map(extract_names)
    df["keywords_list"] = df["keywords"].map(extract_names)
    df["companies_list"] = df["production_companies"].map(extract_names)
    df["countries_list"] = df["production_countries"].map(extract_names)
    df["director"] = df["crew"].map(extract_director)
    df["cast_list"] = df["cast"].map(lambda v: extract_names(v, limit=8))
    df["cast_full"] = df["cast"].map(lambda v: [{"name": p["name"], "character": p.get("character")}
                                                for p in parse_json_list(v)[:20] if isinstance(p, dict) and p.get("name")])
    df["crew_key"] = df["crew"].map(lambda v: [{"name": p["name"], "job": p["job"], "department": p.get("department")}
                                               for p in parse_json_list(v)
                                               if isinstance(p, dict) and p.get("job") in KEY_JOBS and p.get("name")])
    df = df.drop(columns=["genres", "keywords", "production_companies", "production_countries",
                          "cast", "crew"])
    log.info("Dataset loaded: %d movies", len(df))
    return df.reset_index(drop=True)
