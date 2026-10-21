"""Analytics layer: pure functions that take the cleaned DataFrame and return JSON-safe data."""
import math

import numpy as np
import pandas as pd

from config import CURRENCY_NOTE, DATASET_NAME, DEFAULT_MIN_VOTES, ROI_MIN_BUDGET

SORT_FIELDS = {"rating": "vote_average", "popularity": "popularity", "revenue": "revenue",
               "votes": "vote_count", "year": "year", "title": "title", "budget": "budget", "updated": "updated_at"}


def clean(obj):
    """Recursively convert numpy/pandas values to plain Python; NaN/inf -> None."""
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return None if math.isnan(obj) or math.isinf(obj) else round(float(obj), 3)
    return obj


def _rows(df: pd.DataFrame) -> list[dict]:
    return clean(df.to_dict("records"))


# ---------- movie records ----------
def movie_summary(row) -> dict:
    return clean({"id": int(row["id"]), "title": row["title"],
                  "year": None if pd.isna(row["year"]) else int(row["year"]),
                  "genres": row["genres_list"], "rating": row["vote_average"],
                  "votes": row["vote_count"], "popularity": row["popularity"],
                  "revenue": row["revenue"], "budget": row["budget"],
                  "language": row["original_language"], "poster_path": row.get("poster_path")})


# ---------- filtering / ranking ----------
def filter_movies(df, q=None, genre=None, year_from=None, year_to=None, min_rating=None,
                  min_votes=None, sort="popularity", order="desc", language=None) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if q:
        mask &= df["title"].str.contains(q.strip(), case=False, regex=False, na=False)
    if genre:
        g = genre.strip().lower()
        mask &= df["genres_list"].map(lambda lst: g in [x.lower() for x in lst])
    if year_from is not None:
        mask &= df["year"] >= year_from
    if year_to is not None:
        mask &= df["year"] <= year_to
    if min_rating is not None:
        mask &= df["vote_average"] >= min_rating        # NaN (unrated) never matches
    if min_votes is not None:
        mask &= df["vote_count"] >= min_votes
    if language:
        mask &= df["original_language"] == language.strip().lower()
    return df[mask].sort_values(SORT_FIELDS[sort], ascending=(order == "asc"),
                                na_position="last", kind="stable")


def in_period(df, start=None, end=None) -> pd.DataFrame:
    """Restrict to a release-year range (movies without a date are excluded when a range is given)."""
    if start is not None:
        df = df[df["year"] >= start]
    if end is not None:
        df = df[df["year"] <= end]
    return df


def paginate(frame: pd.DataFrame, offset: int, limit: int) -> dict:
    page = frame.iloc[offset: offset + limit]
    return {"total": int(len(frame)), "offset": offset, "limit": limit,
            "items": [movie_summary(r) for _, r in page.iterrows()]}


def top_rated(df, min_votes=DEFAULT_MIN_VOTES, **filters) -> pd.DataFrame:
    """Rank by vote_average (ties broken by vote_count), ignoring movies with too few votes."""
    f = filter_movies(df, min_votes=min_votes, sort="rating", **filters)
    return f.sort_values(["vote_average", "vote_count"], ascending=False, kind="stable")


# ---------- aggregates ----------
def _genre_frame(df):
    g = df[["id", "genres_list", "vote_average", "revenue", "popularity"]].explode("genres_list")
    return g.dropna(subset=["genres_list"]).rename(columns={"genres_list": "genre"})


def genre_stats(df) -> list[dict]:
    """A multi-genre movie counts once in EACH of its genres, so counts sum to more than total movies."""
    out = _genre_frame(df).groupby("genre").agg(
        count=("id", "nunique"), avg_rating=("vote_average", "mean"),
        total_revenue=("revenue", lambda s: s.sum(min_count=1)),
        avg_popularity=("popularity", "mean")).reset_index()
    return _rows(out.sort_values("count", ascending=False))


def year_stats(df, start=None, end=None) -> list[dict]:
    d = df.dropna(subset=["year"])
    if start is not None:
        d = d[d["year"] >= start]
    if end is not None:
        d = d[d["year"] <= end]
    out = d.groupby("year").agg(count=("id", "count"), avg_rating=("vote_average", "mean"),
                                total_revenue=("revenue", lambda s: s.sum(min_count=1))).reset_index()
    out["year"] = out["year"].astype(int)
    return _rows(out)


def rating_stats(df) -> dict:
    rated = df.dropna(subset=["vote_average"])
    counts, edges = np.histogram(rated["vote_average"], bins=np.arange(0, 11))
    bins = [{"range": f"{int(a)}-{int(b)}", "count": int(c)} for a, b, c in zip(edges[:-1], edges[1:], counts)]
    s = rated[rated["vote_count"] >= 50]
    scatter = s[["title", "vote_average", "popularity", "vote_count"]].rename(
        columns={"vote_average": "rating", "vote_count": "votes"})
    most_voted = rated.sort_values("vote_count", ascending=False).head(10)
    return clean({"rated_movies": len(rated), "mean": rated["vote_average"].mean(),
                  "median": rated["vote_average"].median(), "bins": bins,
                  "scatter_note": "movies with >= 50 votes", "scatter": scatter.to_dict("records"),
                  "most_voted": [movie_summary(r) for _, r in most_voted.iterrows()]})


def financial_stats(df) -> dict:
    """Profit = revenue - budget; ROI% = profit / budget * 100. Only where both are known (>0)."""
    both = df.dropna(subset=["budget", "revenue"]).copy()
    both = both[both["budget"] > 0]                      # avoids division by zero (genuine 0 budgets)
    both["profit"] = both["revenue"] - both["budget"]
    both["roi"] = both["profit"] / both["budget"] * 100          # budget > 0 guaranteed (NaN otherwise)

    def stats(s):
        s = s.dropna()
        return {"count": len(s), "mean": s.mean(), "median": s.median(), "min": s.min() if len(s) else None,
                "max": s.max() if len(s) else None}

    def top(frame, col, n=10):
        return [dict(movie_summary(r), profit=r.get("profit"), roi=r.get("roi"))
                for _, r in frame.sort_values(col, ascending=False).head(n).iterrows()]

    def hist(s):       # distribution of known, positive values in $ millions
        labels = ["<$1M", "$1-5M", "$5-10M", "$10-25M", "$25-50M", "$50-100M", "$100-200M", "$200M+"]
        counts, _ = np.histogram(s.dropna()[lambda x: x > 0] / 1e6, bins=[0, 1, 5, 10, 25, 50, 100, 200, 1e6])
        return [{"range": l, "count": int(c)} for l, c in zip(labels, counts)]

    sc = both.sort_values("revenue", ascending=False).head(300)
    return clean({"currency": CURRENCY_NOTE, "budget": stats(df["budget"]), "revenue": stats(df["revenue"]),
                  "movies_with_both": len(both),
                  "formulas": {"estimated_profit": "revenue - budget",
                               "estimated_roi_percent": "(revenue - budget) / budget * 100",
                               "note": f"Simplified metrics, not audited profit. ROI ranking uses budgets >= {ROI_MIN_BUDGET:,}."},
                  "top_revenue": top(df.dropna(subset=["revenue"]), "revenue"),
                  "top_budget": top(df.dropna(subset=["budget"]), "budget"),
                  "top_roi": top(both[both["budget"] >= ROI_MIN_BUDGET], "roi"),
                  "top_profit": top(both, "profit"),
                  "budget_distribution": hist(df["budget"]), "revenue_distribution": hist(df["revenue"]),
                  "scatter": sc[["title", "budget", "revenue"]].to_dict("records")})


def language_stats(df, top_n=15) -> list[dict]:
    out = df.groupby("original_language").agg(count=("id", "count"), avg_rating=("vote_average", "mean")).reset_index()
    return _rows(out.sort_values("count", ascending=False).head(top_n))


def production_stats(df, top_n=15) -> dict:
    def count(col, name):
        c = df[["id", col]].explode(col).dropna(subset=[col]).groupby(col)["id"].nunique()
        return [{name: k, "count": int(v)} for k, v in c.sort_values(ascending=False).head(top_n).items()]
    d = df.dropna(subset=["director"]).groupby("director").agg(
        count=("id", "count"), avg_rating=("vote_average", "mean"),
        total_revenue=("revenue", lambda s: s.sum(min_count=1))).reset_index()
    directors = _rows(d.sort_values(["count", "total_revenue"], ascending=False, na_position="last").head(top_n))
    return {"companies": count("companies_list", "company"), "countries": count("countries_list", "country"),
            "directors": directors}


def summary(df) -> dict:
    rated = df["vote_average"].dropna()
    rev = df["revenue"].dropna()
    tr = top_rated(df)
    pop = df.sort_values("popularity", ascending=False)
    return clean({
        "dataset": DATASET_NAME, "total_movies": len(df), "rated_movies": len(rated),
        "average_popularity": df["popularity"].mean() if len(df) else None,
        "average_rating": rated.mean() if len(rated) else None,
        "total_genres": len(_genre_frame(df)["genre"].unique()),
        "total_revenue": rev.sum() if len(rev) else None, "movies_with_revenue": len(rev),
        "currency": CURRENCY_NOTE,
        "year_min": df["year"].min(), "year_max": df["year"].max(),
        "highest_rated": movie_summary(tr.iloc[0]) if len(tr) else None,
        "most_popular": movie_summary(pop.iloc[0]) if len(pop) else None,
        "notes": {"average_rating": "Movies with zero votes are excluded.",
                  "total_revenue": "Sum of known revenue only; revenue of 0 means unknown and is excluded.",
                  "highest_rated": f"Highest vote_average among movies with >= {DEFAULT_MIN_VOTES} votes."}})


# ---------- movie comparison ----------
def _money(v):
    return f"${v / 1e9:.2f}B" if v >= 1e9 else f"${v / 1e6:.1f}M" if v >= 1e6 else f"${v:,.0f}"


def compare_highlights(movies: list[dict]) -> list[str]:
    """Plain-English summary of how 2+ movie records differ."""
    out = []
    metrics = [("rating", "the highest rating", lambda v: f"{v:.1f}"), ("votes", "the most votes", lambda v: f"{v:,.0f}"),
               ("popularity", "the highest popularity", lambda v: f"{v:.1f}"), ("budget", "the largest budget", _money),
               ("revenue", "the highest revenue", _money), ("runtime", "the longest runtime", lambda v: f"{v:.0f} min")]
    for key, label, fmt in metrics:
        known = [m for m in movies if m.get(key) is not None]
        if len(known) >= 2:
            best = max(known, key=lambda m: m[key])
            if sum(m[key] == best[key] for m in known) == 1:
                out.append(f"{best['title']} has {label} ({fmt(best[key])}).")
        elif len(known) < len(movies):
            out.append(f"{label[4:].capitalize()} cannot be compared: data missing for some movies.")
    years = sorted(m["year"] for m in movies if m.get("year"))
    if len(years) >= 2 and years[0] != years[-1]:
        out.append(f"Release years span {years[0]}-{years[-1]} ({years[-1] - years[0]} years apart).")
    shared = set.intersection(*[set(m["genres"]) for m in movies]) if movies else set()
    out.append("Shared genres: " + ", ".join(sorted(shared)) + "." if shared else "The movies share no genre.")
    return out


# ---------- user-interaction analytics ----------
def interaction_summary(inter: pd.DataFrame, movies: pd.DataFrame) -> dict:
    """Aggregates computed from the interactions table (no private per-user data is returned)."""
    if inter.empty:
        return {"total_interactions": 0, "unique_users": 0}
    inter = inter.copy()
    inter["created_at"] = pd.to_datetime(inter["created_at"], utc=True, errors="coerce")
    t = inter["interaction_type"]
    title = movies.set_index("id")["title"]
    tmdb = movies.set_index("id")["vote_average"]
    genres = movies.set_index("id")["genres_list"]

    def top(frame, n=10):
        vc = frame.groupby("movie_id").size().sort_values(ascending=False).head(n)
        return [{"movie_id": int(k), "title": title.get(k), "count": int(v)} for k, v in vc.items()]

    rated = inter[t == "rating"].dropna(subset=["rating"])
    counts, _ = np.histogram(rated["rating"], bins=np.arange(0.5, 11.5, 1))
    per = rated.groupby("movie_id").agg(count=("rating", "size"), personal=("rating", "mean")) \
        .sort_values("count", ascending=False).head(10)
    engaged = inter[t.isin(["like", "recommendation_click"]) | ((t == "watchlist") & inter["active"])
                    | ((t == "rating") & (inter["rating"] >= 7))]
    g = engaged.assign(genre=engaged["movie_id"].map(genres)).explode("genre").dropna(subset=["genre"])
    g = g.groupby("genre").size().sort_values(ascending=False).head(10)
    daily = inter.dropna(subset=["created_at"]).groupby(inter["created_at"].dt.strftime("%Y-%m-%d")).size().tail(30)
    imp, clk = int((t == "recommendation_impression").sum()), int((t == "recommendation_click").sum())
    fb = inter[t == "recommendation_feedback"]
    relevant = int(sum((m or {}).get("feedback") == "relevant" for m in fb["meta"]))
    wl = inter[t == "watchlist"]
    return clean({
        "total_interactions": len(inter), "unique_users": inter["user_id"].nunique(),
        "by_type": [{"type": k, "count": int(v)} for k, v in t.value_counts().items()],
        "ratings": {"count": len(rated), "average": rated["rating"].mean() if len(rated) else None,
                    "distribution": [{"score": i + 1, "count": int(c)} for i, c in enumerate(counts)],
                    "most_rated": [{"movie_id": int(k), "title": title.get(k), "count": int(r["count"]),
                                    "avg_personal_rating": r["personal"], "tmdb_rating": tmdb.get(k)}
                                   for k, r in per.iterrows()]},
        "likes": {"likes": int((t == "like").sum()), "dislikes": int((t == "dislike").sum()),
                  "top_liked": top(inter[t == "like"])},
        "watchlist": {"active": int(wl["active"].sum()), "removed": int((~wl["active"]).sum()),
                      "top_movies": top(wl[wl["active"]])},
        "genre_engagement": [{"genre": k, "count": int(v)} for k, v in g.items()],
        "daily_activity": [{"date": k, "count": int(v)} for k, v in daily.items()],
        "recommendations": {"impressions": imp, "clicks": clk, "click_through_rate": clk / imp if imp else None,
                            "feedback": len(fb), "relevant": relevant,
                            "relevance_rate": relevant / len(fb) if len(fb) else None},
        "last_interaction": inter["created_at"].max().isoformat() if inter["created_at"].notna().any() else None})
