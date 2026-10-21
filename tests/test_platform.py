import csv
import io
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select, text

import manage
from conftest import login
from database import SessionLocal, engine, invalidate_cache
from models import Interaction, Movie
from partner_client import SharedMovieAPI

DARK_KNIGHT, AVATAR, INCEPTION = 155, 19995, 27205


@pytest.fixture
def app_client():
    from main import app
    return TestClient(app)


def new_user(c):
    """Register a fresh normal user and return (username, auth headers)."""
    name = "user_" + uuid.uuid4().hex[:8]
    assert c.post("/api/users/register", json={"username": name, "password": "password-123"}).status_code == 201
    r = c.post("/api/auth/login", json={"username": name, "password": "password-123"}).json()
    assert r["role"] == "user"
    return name, {"Authorization": "Bearer " + r["token"]}


def post(c, h, mid, t, **kw):
    return c.post("/api/interactions", json={"movie_id": mid, "interaction_type": t, **kw}, headers=h)


# ---------- accounts and permissions ----------
def test_register_rules(app_client):
    assert app_client.post("/api/users/register", json={"username": "alice", "password": "password-123"}).status_code == 409
    assert app_client.post("/api/users/register", json={"username": "ab", "password": "password-123"}).status_code == 422
    assert app_client.post("/api/users/register", json={"username": "okname", "password": "short"}).status_code == 422
    name, _ = new_user(app_client)
    assert app_client.post("/api/users/register", json={"username": name, "password": "password-123"}).status_code == 409


def test_normal_user_cannot_edit_or_export(app_client):
    _, h = new_user(app_client)
    assert app_client.patch(f"/api/movies/{AVATAR}", json={"vote_average": 1}, headers=h).status_code == 403
    assert app_client.get("/api/export/movies.csv", headers=h).status_code == 403
    assert app_client.get("/api/data/quality", headers=h).status_code == 403
    assert post(app_client, {}, AVATAR, "like").status_code == 401           # anonymous cannot record interactions


# ---------- interaction semantics ----------
def test_rating_upsert_and_validation(app_client):
    _, h = new_user(app_client)
    r = post(app_client, h, DARK_KNIGHT, "rating", rating=9)
    assert r.status_code == 201 and r.json()["rating"] == 9
    r2 = post(app_client, h, DARK_KNIGHT, "rating", rating=7.5)             # same slot -> updated, not duplicated
    assert r2.status_code == 200 and r2.json()["id"] == r.json()["id"] and r2.json()["rating"] == 7.5
    mine = app_client.get("/api/interactions?interaction_type=rating", headers=h).json()
    assert mine["total"] == 1
    for bad in [dict(interaction_type="rating"), dict(interaction_type="rating", rating=11), dict(interaction_type="rating", rating=0),
                dict(interaction_type="like", rating=5), dict(interaction_type="dance"),
                dict(interaction_type="like", metadata={"x": "y" * 3000})]:
        assert app_client.post("/api/interactions", json={"movie_id": DARK_KNIGHT, **bad}, headers=h).status_code == 422
    assert post(app_client, h, 987654321, "like").status_code == 404


def test_like_dislike_replace_each_other(app_client):
    _, h = new_user(app_client)
    post(app_client, h, AVATAR, "like")
    r = post(app_client, h, AVATAR, "dislike")
    assert r.status_code == 200 and r.json()["interaction_type"] == "dislike"
    assert app_client.get("/api/interactions", headers=h).json()["total"] == 1


def test_watchlist_semantics(app_client):
    name, h = new_user(app_client)
    assert post(app_client, h, INCEPTION, "watchlist_remove").status_code == 404      # never added
    assert post(app_client, h, INCEPTION, "watchlist_add").status_code == 201
    assert post(app_client, h, INCEPTION, "watchlist_add").status_code == 200        # no duplicate
    wl = app_client.get(f"/api/users/{name}/watchlist", headers=h).json()
    assert wl["count"] == 1 and wl["items"][0]["title"] == "Inception"
    assert post(app_client, h, INCEPTION, "watchlist_remove").json()["active"] is False
    assert app_client.get(f"/api/users/{name}/watchlist", headers=h).json()["count"] == 0
    assert post(app_client, h, INCEPTION, "watchlist_add").json()["active"] is True   # can come back


def test_privacy(app_client, alice):
    a, ha = new_user(app_client)
    b, hb = new_user(app_client)
    post(app_client, ha, AVATAR, "rating", rating=8)
    assert app_client.get(f"/api/users/{a}/ratings", headers=hb).status_code == 403
    assert app_client.get(f"/api/users/{a}/watchlist", headers=hb).status_code == 403
    assert app_client.get(f"/api/interactions?user_id={a}", headers=hb).status_code == 403
    assert all(i["user_id"] == b for i in app_client.get("/api/interactions", headers=hb).json()["items"])
    assert app_client.get(f"/api/users/{a}/ratings").status_code == 401
    assert app_client.get(f"/api/users/{a}/ratings", headers=alice).json()["count"] == 1      # editor may audit
    iid = app_client.get("/api/interactions", headers=ha).json()["items"][0]["id"]
    assert app_client.delete(f"/api/interactions/{iid}", headers=hb).status_code == 403
    assert app_client.delete(f"/api/interactions/{iid}", headers=ha).status_code == 200


def test_recommendation_events_and_feedback(app_client):
    _, h = new_user(app_client)
    before = app_client.get("/api/interactions/summary").json().get("recommendations", {"impressions": 0, "clicks": 0, "feedback": 0})
    post(app_client, h, INCEPTION, "recommendation_impression", metadata={"source_movie_id": DARK_KNIGHT})
    post(app_client, h, INCEPTION, "recommendation_impression", metadata={"source_movie_id": DARK_KNIGHT})   # events append
    post(app_client, h, INCEPTION, "recommendation_click")
    r = app_client.post("/api/recommendation-feedback", headers=h,
                        json={"movie_id": INCEPTION, "feedback": "relevant", "source_movie_id": DARK_KNIGHT, "algorithm": "demo"})
    assert r.status_code == 201 and r.json()["metadata"]["feedback"] == "relevant"
    assert app_client.post("/api/recommendation-feedback", headers=h, json={"movie_id": INCEPTION, "feedback": "maybe"}).status_code == 422
    rec = app_client.get("/api/interactions/summary").json()["recommendations"]
    assert rec["impressions"] == before["impressions"] + 2 and rec["clicks"] == before["clicks"] + 1
    assert rec["feedback"] == before["feedback"] + 1 and 0 <= rec["click_through_rate"]


# ---------- integration test 2: personal rating -> engagement analytics, TMDB rating untouched ----------
def test_personal_rating_feeds_analytics_without_touching_tmdb_rating(app_client):
    tmdb_before = app_client.get(f"/api/movies/{AVATAR}").json()["rating"]
    s0 = app_client.get("/api/interactions/summary").json()
    _, h = new_user(app_client)
    post(app_client, h, AVATAR, "rating", rating=10)
    post(app_client, h, AVATAR, "watchlist_add")
    s1 = app_client.get("/api/interactions/summary").json()
    assert s1["total_interactions"] == s0["total_interactions"] + 2
    assert s1["ratings"]["count"] == s0.get("ratings", {"count": 0})["count"] + 1
    assert s1["ratings"]["distribution"][9]["count"] >= 1                       # score 10 bucket
    assert any(m["movie_id"] == AVATAR and m["avg_personal_rating"] is not None for m in s1["ratings"]["most_rated"])
    assert any(g["genre"] == "Action" for g in s1["genre_engagement"])
    assert app_client.get(f"/api/movies/{AVATAR}").json()["rating"] == tmdb_before   # aggregate TMDB rating unchanged
    with SessionLocal() as s:
        assert s.get(Movie, AVATAR).vote_average == tmdb_before


# ---------- integration test 1: Client A edits, Client B reads, analytics + CSV ----------
def test_client_a_edit_visible_to_client_b_analytics_and_csv(alice):
    from main import app
    A, B = TestClient(app), TestClient(app)
    mid = 278                                                    # The Shawshank Redemption
    original = B.get(f"/api/movies/{mid}").json()
    a_view = A.get(f"/api/movies/{mid}").json()
    assert a_view["title"] == original["title"]
    r = A.patch(f"/api/movies/{mid}", json={"vote_average": 2.0, "overview": "Edited by client A."}, headers=alice)
    assert r.status_code == 200
    seen = B.get(f"/api/movies/{mid}").json()
    assert seen["rating"] == 2.0 and seen["overview"] == "Edited by client A."
    assert mid not in [m["id"] for m in B.get("/api/movies/top-rated?limit=50").json()["items"]]
    drama = next(g for g in B.get("/api/analytics/genres").json()["genres"] if g["genre"] == "Drama")
    A.patch(f"/api/movies/{mid}", json={"vote_average": original["rating"]}, headers=alice)
    drama_back = next(g for g in B.get("/api/analytics/genres").json()["genres"] if g["genre"] == "Drama")
    assert drama["avg_rating"] < drama_back["avg_rating"]                       # analytics recalculated both ways
    A.patch(f"/api/movies/{mid}", json={"overview": "Marker overview 777"}, headers=alice)
    row = next(r for r in csv.DictReader(io.StringIO(A.get("/api/export/movies.csv", headers=alice).text)) if r["id"] == str(mid))
    assert row["overview"] == "Marker overview 777" and "poster_path" in row


def test_cache_invalidation_search_uses_new_title(app_client, alice):
    app_client.patch(f"/api/movies/{INCEPTION}", json={"title": "Zzyzx Renamed Film"}, headers=alice)
    assert app_client.get("/api/movies/search?q=zzyzx").json()["total"] == 1
    app_client.patch(f"/api/movies/{INCEPTION}", json={"title": "Inception"}, headers=alice)
    assert app_client.get("/api/movies/search?q=zzyzx").json()["total"] == 0


def test_data_persists_across_simulated_restart(alice):
    from main import app
    c = TestClient(app)
    name, h = new_user(c)
    c.patch(f"/api/movies/{AVATAR}", json={"overview": "persisted text"}, headers=alice)
    post(c, h, AVATAR, "rating", rating=6)
    engine.dispose()                      # drop all connections, as a process restart would
    invalidate_cache()                    # forget the in-memory snapshot
    after = TestClient(app)               # a brand-new client
    assert after.get(f"/api/movies/{AVATAR}").json()["overview"] == "persisted text"
    assert after.get(f"/api/users/{name}/ratings", headers=h).json()["items"][0]["personal_rating"] == 6


# ---------- analytics: period filter, language, compare, directors, data quality ----------
def test_period_filter_and_empty_period(app_client):
    full = app_client.get("/api/analytics/summary").json()
    p = app_client.get("/api/analytics/summary?start=2000&end=2009").json()
    assert 0 < p["total_movies"] < full["total_movies"] and p["catalogue_total"] == full["total_movies"]
    assert p["average_popularity"] is not None and full["last_updated"]
    for path in ["genres", "ratings", "financials", "languages", "production", "summary"]:
        r = app_client.get(f"/api/analytics/{path}?start=1900&end=1901")        # empty period must not crash
        assert r.status_code == 200 and "NaN" not in r.text
    assert app_client.get("/api/analytics/genres?start=2010&end=2000").status_code == 400


def test_language_filter_directors_and_financial_extras(app_client):
    fr = app_client.get("/api/movies?language=fr&limit=100").json()
    assert fr["total"] > 0 and all(m["language"] == "fr" for m in fr["items"])
    prod = app_client.get("/api/analytics/production").json()
    assert prod["directors"] and prod["directors"][0]["count"] >= prod["directors"][-1]["count"]
    f = app_client.get("/api/analytics/financials").json()
    assert len(f["budget_distribution"]) == 8 and f["top_profit"][0]["profit"] >= f["top_profit"][1]["profit"]


def test_compare(app_client):
    r = app_client.get(f"/api/analytics/compare?ids={AVATAR},{DARK_KNIGHT},{INCEPTION}").json()
    assert [m["id"] for m in r["movies"]] == [AVATAR, DARK_KNIGHT, INCEPTION]
    assert any("Avatar has the highest revenue" in h for h in r["highlights"])
    assert app_client.get(f"/api/analytics/compare?ids={AVATAR}").status_code == 422
    assert app_client.get("/api/analytics/compare?ids=1,2,3,4,5").status_code == 422
    assert app_client.get("/api/analytics/compare?ids=a,b").status_code == 422
    assert app_client.get(f"/api/analytics/compare?ids={AVATAR},987654321").status_code == 404


def test_data_quality_editor_only(app_client, alice):
    assert app_client.get("/api/data/quality").status_code == 401
    q = app_client.get("/api/data/quality", headers=alice).json()
    assert q["total"] >= 4803 and q["with_poster"] >= 0 and q["missing_budget"] > 0 and "recent_edits" in q


# ---------- posters (mocked TMDB: the real service is not reachable from the test environment) ----------
def test_poster_enrichment_is_cached_and_safe():
    calls = []

    def fake(mid):
        calls.append(mid)
        if mid == 1: raise manage.TmdbTransient("boom")
        return None if mid % 2 else f"/poster_{mid}.jpg"

    with SessionLocal() as s:
        ids = list(s.scalars(select(Movie.id).where(Movie.poster_checked_at.is_(None)).order_by(Movie.popularity.desc()).limit(6)))
        stats = manage.enrich_posters(s, fetch=fake, limit=6, delay=0)
        assert stats["checked"] == 6 and stats["found"] + stats["no_poster"] == 6
        found = s.scalars(select(Movie).where(Movie.poster_path.is_not(None))).first()
        assert found.poster_path == f"/poster_{found.id}.jpg" and found.poster_checked_at is not None
        first_calls = len(calls)
        manage.enrich_posters(s, fetch=fake, limit=6, delay=0)           # cached: the same movies are not asked again
        assert not set(calls[first_calls:]) & set(ids)
    assert TestClient(__import__("main").app).get(f"/api/movies/{found.id}").json()["poster_path"] == found.poster_path


def test_poster_transient_error_not_cached():
    def down(_):
        raise manage.TmdbTransient("offline")
    with SessionLocal() as s:
        before = s.scalar(select(func.count(Movie.id)).where(Movie.poster_checked_at.is_(None)))
        assert manage.enrich_posters(s, fetch=down, limit=10, delay=0)["errors"] == 5
        assert s.scalar(select(func.count(Movie.id)).where(Movie.poster_checked_at.is_(None))) == before


def test_missing_tmdb_credentials_are_reported(monkeypatch):
    monkeypatch.delenv("TMDB_READ_TOKEN", raising=False)
    monkeypatch.delenv("TMDB_API_KEY", raising=False)
    with pytest.raises(manage.TmdbTransient):
        manage.tmdb_fetch_poster(155)


def test_schema_upgrade_adds_poster_columns(tmp_path):
    old = create_engine(f"sqlite:///{(tmp_path / 'old.db').as_posix()}")
    with old.begin() as c:
        c.execute(text("create table movies (id integer primary key, title varchar(300))"))
        c.execute(text("insert into movies values (1, 'Old row')"))
    assert manage.ensure_columns(old) == ["poster_path", "poster_checked_at"]
    assert manage.ensure_columns(old) == []                                  # safe to repeat
    with old.connect() as c:
        assert c.execute(text("select title, poster_path from movies")).one() == ("Old row", None)


# ---------- the partner's example client through the shared API ----------
def test_partner_client_round_trip(alice):
    from main import app
    mine, theirs = TestClient(app), TestClient(app)                           # two independent clients
    partner = SharedMovieAPI("http://testserver", http=theirs)
    name = "partner_" + uuid.uuid4().hex[:6]
    partner.register(name, "password-123")
    partner.login(name, "password-123")
    assert partner.movie(DARK_KNIGHT)["title"] == "The Dark Knight"
    partner.rate(DARK_KNIGHT, 9)
    partner.watchlist_add(DARK_KNIGHT)
    partner.recommendation_shown(INCEPTION, source_movie_id=DARK_KNIGHT, algorithm="demo")
    partner.recommendation_clicked(INCEPTION, source_movie_id=DARK_KNIGHT, algorithm="demo")
    partner.recommendation_feedback(INCEPTION, True, source_movie_id=DARK_KNIGHT)
    assert partner.my_ratings()["items"][0]["personal_rating"] == 9 and partner.my_watchlist()["count"] == 1
    s = mine.get("/api/interactions/summary").json()                          # my dashboard's view of the partner's activity
    assert s["recommendations"]["clicks"] >= 1 and s["watchlist"]["active"] >= 1
    with pytest.raises(Exception):
        partner.patch_movie(DARK_KNIGHT, vote_average=1)                      # users cannot edit metadata
    # reverse direction: my editor edit is visible to the partner client
    mine.patch(f"/api/movies/{DARK_KNIGHT}", json={"tagline": None, "runtime": 152}, headers=alice)
    assert partner.movie(DARK_KNIGHT)["runtime"] == 152
