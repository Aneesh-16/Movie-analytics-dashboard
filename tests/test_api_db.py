import csv
import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text

import manage
from conftest import login
from database import SessionLocal, engine
from models import Movie

AVATAR = 19995


def rating(c, mid=AVATAR):
    return c.get(f"/api/movies/{mid}").json()["rating"]


# ---------- database, import ----------
def test_health_schema_and_import():
    from main import app
    h = TestClient(app).get("/api/health").json()
    assert h == {"status": "ok", "database": "connected", "dataset_imported": True, "movies": 4803}
    with engine.connect() as conn:
        assert conn.execute(select(func.count(Movie.id))).scalar() == 4803


def test_import_stores_null_for_unknown_and_json_fields():
    with SessionLocal() as s:
        zero_budget = s.scalars(select(Movie).where(Movie.budget.is_(None))).first()
        assert zero_budget is not None                       # TMDB 0 -> NULL (unknown)
        a = s.get(Movie, AVATAR)
        assert a.director == "James Cameron" and a.genres[0] == "Action" and a.cast_members[0]["name"]
        assert any(c["job"] == "Director" for c in a.crew_members) and a.year == 2009


def test_reimport_no_duplicates_and_keeps_edits(client, alice):
    original = rating(client)
    client.patch(f"/api/movies/{AVATAR}", json={"vote_average": 3.3}, headers=alice)
    with SessionLocal() as s:
        result = manage.import_csv(s)
        assert result["inserted"] == 0 and result["already_present"] == 4803
        assert s.scalar(select(func.count(Movie.id))) == 4803
    assert rating(client) == 3.3                              # edit NOT overwritten by re-import
    client.patch(f"/api/movies/{AVATAR}", json={"vote_average": original}, headers=alice)


def test_import_missing_file(tmp_path):
    from data_loader import DatasetError
    with SessionLocal() as s, pytest.raises(DatasetError):
        manage.import_csv(s, tmp_path / "x.csv", tmp_path / "y.csv")


# ---------- reads ----------
def test_summary_and_analytics_endpoints(client):
    s = client.get("/api/analytics/summary").json()
    assert s["total_movies"] == 4803 and 5 < s["average_rating"] < 7
    for p in ["genres", "years", "ratings", "financials", "languages", "production"]:
        r = client.get("/api/analytics/" + p)
        assert r.status_code == 200 and "NaN" not in r.text and "Infinity" not in r.text


def test_list_search_filter_pagination(client):
    a = client.get("/api/movies?limit=5&sort=rating").json()
    b = client.get("/api/movies?limit=5&offset=5&sort=rating").json()
    assert a["total"] == 4803 and len(a["items"]) == 5 and a["items"][0]["id"] != b["items"][0]["id"]
    r = client.get("/api/movies/search?q=batman&year_from=2000&year_to=2020&min_rating=7").json()
    assert r["total"] > 0 and all("batman" in m["title"].lower() for m in r["items"])
    assert client.get("/api/movies/search?q=zzzzqqq").json()["items"] == []
    assert client.get("/api/movies?year_from=2010&year_to=2000").status_code == 400
    assert client.get("/api/movies?limit=1000").status_code == 422
    t = client.get("/api/movies/top-rated?limit=3").json()["items"]
    assert t[0]["rating"] >= t[1]["rating"] and all(m["votes"] >= 500 for m in t)


def test_detail_and_missing(client):
    d = client.get(f"/api/movies/{AVATAR}").json()
    assert d["title"] == "Avatar" and d["cast"] and d["director"] == "James Cameron"
    assert client.get("/api/movies/-1").status_code == 404
    assert client.get("/api/movies/abc").status_code == 422


# ---------- authentication ----------
def test_unauthorized_writes_and_bad_logins(client):
    body = {"vote_average": 5}
    assert client.patch(f"/api/movies/{AVATAR}", json=body).status_code == 401
    assert client.patch(f"/api/movies/{AVATAR}", json=body, headers={"Authorization": "Bearer junk"}).status_code == 401
    assert client.post("/api/movies", json={"id": 999001, "title": "X"}).status_code == 401
    assert client.get("/api/export/movies.csv").status_code == 401
    assert client.post("/api/auth/login", json={"username": "alice", "password": "wrong"}).status_code == 401
    assert client.post("/api/auth/login", json={"username": "nobody", "password": "whatever1"}).status_code == 401
    tok = login(client)["Authorization"]
    tampered = tok[:-3] + ("aaa" if not tok.endswith("aaa") else "bbb")
    assert client.get("/api/auth/me", headers={"Authorization": tampered}).status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": tok}).json() == {"username": "alice", "role": "editor"}


def test_password_not_stored_in_plain_text():
    from models import Editor
    with SessionLocal() as s:
        h = s.scalar(select(Editor.password_hash).where(Editor.username == "alice"))
    assert h.startswith("scrypt$") and "alice-password-1" not in h


# ---------- writes ----------
def test_valid_patch_persists_in_database(client, alice):
    r = client.patch(f"/api/movies/{AVATAR}", json={"vote_average": 8.4, "overview": "Updated overview."}, headers=alice)
    assert r.status_code == 200 and r.json()["rating"] == 8.4 and r.json()["last_edited_by"] == "alice"
    with SessionLocal() as s:                                  # brand-new session straight to the database
        m = s.get(Movie, AVATAR)
        assert m.vote_average == 8.4 and m.overview == "Updated overview."
    assert client.get(f"/api/movies/{AVATAR}").json()["overview"] == "Updated overview."


@pytest.mark.parametrize("payload", [
    {"vote_average": 11}, {"vote_average": -1}, {"vote_average": "abc"}, {"release_date": "not-a-date"},
    {"release_date": "1500-01-01"}, {"id": 5}, {"vote_count": 10}, {"director": "X"}, {"title": ""},
    {"title": None}, {"budget": -5}, {"original_language": "English"}, {"genres": ["ok", ""]}, {"runtime": 99999},
    {"title": "x" * 301}])
def test_invalid_payloads_rejected(client, alice, payload):
    before = client.get(f"/api/movies/{AVATAR}").json()
    assert client.patch(f"/api/movies/{AVATAR}", json=payload, headers=alice).status_code == 422
    assert client.get(f"/api/movies/{AVATAR}").json()["updated_at"] == before["updated_at"]   # nothing saved


def test_patch_empty_and_nonexistent(client, alice):
    assert client.patch(f"/api/movies/{AVATAR}", json={}, headers=alice).status_code == 400
    assert client.patch("/api/movies/987654321", json={"vote_average": 5}, headers=alice).status_code == 404


def test_genuine_zero_vs_unknown_and_no_division_by_zero(client, alice):
    with SessionLocal() as s:
        mid = s.scalars(select(Movie.id).where(Movie.budget.is_(None)).limit(1)).first()
    assert client.get(f"/api/movies/{mid}").json()["budget"] is None
    r = client.patch(f"/api/movies/{mid}", json={"budget": 0, "revenue": 1000}, headers=alice).json()
    assert r["budget"] == 0 and r["revenue"] == 1000                     # genuine 0 kept, not turned into null
    f = client.get("/api/analytics/financials")
    assert f.status_code == 200 and "Infinity" not in f.text and "NaN" not in f.text


def test_create_movie(client, alice):
    new = {"id": 9990001, "title": "Brand New Test Film", "genres": ["Drama"], "vote_average": 7.7,
           "release_date": "2020-02-02"}
    r = client.post("/api/movies", json=new, headers=alice)
    assert r.status_code == 201 and r.json()["year"] == 2020
    assert client.post("/api/movies", json=new, headers=alice).status_code == 409
    assert client.post("/api/movies", json={"id": 0, "title": "bad"}, headers=alice).status_code == 422
    found = client.get("/api/movies/search?q=brand new test").json()
    assert found["total"] == 1 and found["items"][0]["id"] == 9990001


# ---------- the integration test: edit -> read -> analytics -> export ----------
def test_edit_flows_through_reads_analytics_and_export(client, alice):
    mid = 424                                                    # Schindler's List (a top-rated, high-vote movie)
    before_rating = rating(client, mid)
    avg_before = client.get("/api/analytics/summary").json()["average_rating"]
    drama_before = next(g for g in client.get("/api/analytics/genres").json()["genres"] if g["genre"] == "Drama")

    # 1-2. update through PATCH
    assert client.patch(f"/api/movies/{mid}", json={"vote_average": 1.0}, headers=alice).status_code == 200
    # 3-4. a NEW client / request sees it
    fresh = TestClient(client.app)
    assert rating(fresh, mid) == 1.0 and before_rating != 1.0
    # search + top-rated use the updated record
    assert all(m["rating"] >= 7 for m in fresh.get("/api/movies/search?q=schindler&min_rating=7").json()["items"]) is True
    assert mid not in [m["id"] for m in fresh.get("/api/movies/top-rated?limit=50").json()["items"]]
    # 5. analytics recalculated
    assert fresh.get("/api/analytics/summary").json()["average_rating"] < avg_before
    drama_after = next(g for g in fresh.get("/api/analytics/genres").json()["genres"] if g["genre"] == "Drama")
    assert drama_after["avg_rating"] < drama_before["avg_rating"]
    # 6. CSV export from the database contains the new value
    resp = client.get("/api/export/movies.csv", headers=alice)
    assert resp.status_code == 200 and "text/csv" in resp.headers["content-type"]
    row = next(r for r in csv.DictReader(io.StringIO(resp.text)) if r["id"] == str(mid))
    assert float(row["vote_average"]) == 1.0 and row["last_edited_by"] == "alice"
    cr = client.get("/api/export/credits.csv", headers=alice)
    assert cr.status_code == 200 and cr.text.startswith("movie_id,title,cast,crew")
    # restore + confirm analytics follow again
    client.patch(f"/api/movies/{mid}", json={"vote_average": before_rating}, headers=alice)
    assert mid in [m["id"] for m in client.get("/api/movies/top-rated?limit=50").json()["items"]]


# ---------- two independent clients (the partner scenario) ----------
def test_two_independent_clients_and_two_editors():
    from main import app
    app_client, partner_client = TestClient(app), TestClient(app)     # separate clients, no shared state
    a = login(app_client, "alice", "alice-password-1")
    b = login(partner_client, "bob", "bob-password-22")
    original = rating(partner_client)
    # my app edits -> partner app reads
    app_client.patch(f"/api/movies/{AVATAR}", json={"vote_average": 6.6}, headers=a)
    assert rating(partner_client) == 6.6
    # partner edits -> my app reads
    r = partner_client.patch(f"/api/movies/{AVATAR}", json={"vote_average": 7.1}, headers=b)
    assert r.json()["last_edited_by"] == "bob"
    assert rating(app_client) == 7.1
    # a completely separate database connection sees the same stored value
    with engine.connect() as conn:
        assert conn.execute(text("select vote_average from movies where id=:i"), {"i": AVATAR}).scalar() == 7.1
    app_client.patch(f"/api/movies/{AVATAR}", json={"vote_average": original}, headers=a)
