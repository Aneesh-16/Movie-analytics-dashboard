# Movie Intelligence Platform (Movie Analytics Dashboard v3)

One shared PostgreSQL database and one FastAPI service. My analytics dashboard and my partner's recommendation app both talk to that same API, using the same TMDB movie ids.

```
TMDB CSV files ──(one-time: manage.py import-csv)──> Shared PostgreSQL (Supabase)
                                                        │
                                     One shared FastAPI service (Render)  /api/...
                                      ├── My Analytics Dashboard (served at "/")
                                      └── Partner's Recommendation app (same API_BASE_URL)
 Both read the latest movies, edit metadata (editors), and write interactions
 (ratings, likes, watchlist, recommendation clicks/feedback) into the same database.
```

| Piece | Owner / role |
|---|---|
| CSV files | Frozen starting data and backup. Never changed by the app. |
| PostgreSQL | Single source of truth: `movies`, `editors`, `app_users`, `interactions`. |
| FastAPI service | Only code that touches the database. Validation, auth, analytics, export. |
| Analytics dashboard (`frontend.py`) | Mine. Analytics, comparison, data management, engagement analytics. |
| Recommendation app | Partner's. Recommendation logic stays in their project; they use this API. This service has **no** recommendation endpoint. |

## What has been tested, and what has not
**Tested (executed):**
- 59 pytest tests pass on SQLite and on a local PostgreSQL 16.
- Live run on PostgreSQL: a v2-schema database was upgraded by `init-db`, the CSV import was repeated safely, and the dashboard's real JavaScript was driven in jsdom (Chart.js stubbed). All nine pages loaded; period filter, search filters, comparison, user registration, rating, watchlist, editor edit with validation and the Data Management page all worked, with no JavaScript errors.

**Not tested (needs credentials, a browser or your partner):**
- Supabase and Render.
- The live TMDB poster lookup. The enrichment code is tested only with a mocked TMDB, because the TMDB API is unreachable from the build environment.
- Real Chart.js rendering and the visual match to the mockup in an actual browser.
- Your partner's actual application. Cross-application behaviour was verified with independent API clients and the example client in `partner_client.py`.

## Python-only assembly (final review)
Files needed: `config.py, models.py, analytics.py, database.py, schemas.py, auth.py, data_loader.py, api.py, interactions.py, frontend.py, main.py, manage.py, requirements.txt` (+ the two CSVs in `data/` for the one-time import; `partner_client.py` is for the partner; `tests/` is optional).
Dependency order: `config` -> `models` -> `analytics` -> `database` -> `schemas` -> `auth` -> `data_loader` -> `api` + `interactions` -> `frontend` -> `main` (`manage.py` is the command-line tool).

## Local demo (SQLite, no cloud needed)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py init-db
python manage.py import-csv
python manage.py create-editor alice
uvicorn main:app --reload          # http://127.0.0.1:8000    docs: /docs
```
With no `DATABASE_URL` the app uses `local_dev.db` (SQLite). Upgrading from v2: just run `python manage.py init-db` (adds the new columns/tables, never drops data).

## Database
- `movies`: TMDB `id` (primary key), title, original_title, overview, tagline, status, release_date, year, vote_average, vote_count, popularity, budget, revenue, runtime, original_language, genres / keywords / production_companies / production_countries (JSONB name lists), director, cast_members (top 20 `{name, character}`), crew_members (key crew `{name, job, department}`), **poster_path**, poster_checked_at, created_at, updated_at, last_edited_by.
- `editors`, `app_users`: username + salted scrypt hash.
- `interactions`: id, user_id, movie_id (FK to movies), interaction_type, slot, rating, active, metadata (JSONB), created_at, updated_at. Unique on (user_id, movie_id, slot). Indexed on user_id, movie_id and (movie_id, type).
- Unknown vs zero: TMDB's 0 for budget/revenue/runtime is stored as NULL (unknown); a 0 entered by an editor is a genuine 0. Movies with 0 votes have a NULL rating.
- Interactions never touch `movies.vote_average`; a personal rating is a separate row.

## Posters (TMDB)
The CSVs contain no poster information, so `poster_path` is filled by an optional one-off job using the official TMDB API:
```
set TMDB_READ_TOKEN=...            (or TMDB_API_KEY=...)      <- server/CLI only, never in the browser
python manage.py enrich-posters --limit 200      (repeat; each movie is only asked once)
python manage.py enrich-posters --retry-missing  (re-ask movies that had no poster)
```
- Matching is by TMDB **id** (no title guessing), so similar titles cannot get the wrong poster.
- `poster_checked_at` caches the attempt; temporary errors (network, rate limit, bad key) are not cached and the job stops after 5 errors.
- The browser loads images from `https://image.tmdb.org/t/p/w342<poster_path>`. A generated placeholder is shown when there is no poster or the image fails to load.
- Attribution is shown in the sidebar ("This product uses the TMDB API but is not endorsed or certified by TMDB"). Review TMDB's terms and logo guidelines for your use before the demo.

## Authentication and identity
- Public reads (movies, analytics, aggregate interaction summary).
- **Editors** (`manage.py create-editor NAME`; create one per student): PATCH/POST movies, CSV export, data-quality page, and they may read any user's interactions.
- **Users** (`POST /api/users/register`, then `POST /api/auth/login`): record their own interactions and read only their own history. A user id is simply the registered username. No e-mail verification, so a user is an account, not a verified real person. Anonymous activity is not accepted.
- Tokens are HMAC-signed bearer tokens (8 h), sent as `Authorization: Bearer ...`. Secrets only come from environment variables; `.env` is git-ignored.
- Use HTTPS in deployment (Render provides it). Set `CORS_ORIGINS` to your real frontend origins; with a hosted PostgreSQL database cross-origin access is **off** unless you set it. There is no login rate-limiting and registration is open, so use this for the assessment only.

## API contract (base URL = `API_BASE_URL`; interactive docs at `/docs`)
Errors are JSON `{"detail": ...}`: 400 bad range, 401 not logged in/invalid token, 403 not allowed, 404 not found, 409 duplicate, 422 invalid input, 503 database unavailable/not imported.

| Endpoint | Notes |
|---|---|
| GET /api/health | `{status, database, dataset_imported, movies}` |
| GET /api/movies, /api/movies/search | `q, genre, language, year_from, year_to, min_rating, min_votes, sort (rating/popularity/revenue/votes/year/title/budget/updated), order, offset, limit (1-100)` -> `{total, offset, limit, items[]}` |
| GET /api/movies/top-rated | `min_votes (default 500), genre, year_from, year_to, offset, limit`; rule: highest vote_average, ties by votes |
| GET /api/movies/popular | `genre, offset, limit` |
| GET /api/movies/{id} | full record from the database |
| POST /api/movies, PATCH /api/movies/{id} | editor. Editable: title, overview, genres, release_date, vote_average (0-10), popularity, budget, revenue, runtime, original_language. Everything else (id, vote_count, director, cast, crew, poster_path, timestamps) is rejected with 422 |
| GET /api/analytics/summary, genres, ratings, financials, languages, production | optional `start`, `end` (release-year period) |
| GET /api/analytics/years | `start`, `end` |
| GET /api/analytics/compare?ids=1,2,3 | 2-4 movies + plain-English differences |
| GET /api/data/quality | editor: field coverage, recent edits |
| GET /api/export/movies.csv, /api/export/credits.csv | editor; generated from the database |
| POST /api/users/register, POST /api/auth/login, GET /api/auth/me | accounts |
| POST /api/interactions | see below; 201 new row, 200 existing row updated |
| GET /api/interactions | your own (editors: all; filters `movie_id, interaction_type, user_id, offset, limit`) |
| DELETE /api/interactions/{id} | owner or editor |
| GET /api/interactions/summary | public aggregates only (no user ids) |
| GET /api/users/{user_id}/watchlist, /ratings | owner or editor |
| POST /api/recommendation-feedback | `{movie_id, feedback: "relevant"/"not_relevant", source_movie_id?, algorithm?, comment?}` |

Movie list item: `id, title, year, genres, rating, votes, popularity, revenue, budget, language, poster_path`. The detail record adds `release_date, runtime, overview, tagline, status, director, cast, crew, production_companies, production_countries, keywords, updated_at, last_edited_by, estimated_profit` and the aliases `vote_average`, `vote_count`. PATCH bodies use database field names (`vote_average`).

**Interaction rules** (`interaction_type`): `rating` (needs `rating` 1-10, one row per user+movie, updated in place), `like` / `dislike` (one reaction row per user+movie; the newer replaces the older), `watchlist_add` / `watchlist_remove` (one row per user+movie; removal sets `active=false` and keeps the row; removing something never added returns 404), and the append-only events `recommendation_impression`, `recommendation_click`, `recommendation_feedback`. Optional `metadata` (<= 2000 chars) such as `{"source_movie_id": 155, "algorithm": "..."}`. CTR in the dashboard = recorded clicks / recorded impressions; nothing is inferred.

## Data-exchange scenarios (all covered by automated tests)
A. I edit a movie -> saved to PostgreSQL -> the partner's client reads the new value -> analytics change.
B. The partner (as an editor) PATCHes -> my dashboard reads it after Refresh.
C. A user rates in the partner app (`POST /api/interactions`) -> User Engagement page shows it; `vote_average` is untouched.
D. The partner records impressions/clicks/feedback -> my dashboard shows CTR and relevance from those records only.
Refresh strategy: the dashboard's Refresh button (and every page navigation) re-fetches from the API; the partner re-fetches the same way. Search/analytics use a snapshot rebuilt whenever the database's row count or latest `updated_at` changes, so edits are never stale; details and writes go straight to the database.

## Partner integration
Give them: the deployed URL (`API_BASE_URL`), `/docs`, this contract and `partner_client.py` (`SharedMovieAPI(base_url)`: `register/login`, `movies`, `movie`, `rate`, `like`, `watchlist_add`, `recommendation_shown/clicked/feedback`, `my_watchlist`, ...). Both apps use the same TMDB ids. They must not keep a database or CSV copy. If their frontend is on another origin, add that origin to `CORS_ORIGINS`. For lab reliability, a single deployed service is simpler than two apps each loading data.

## Cloud setup (not done yet; needs your accounts)
1. **Supabase:** create a project, copy the connection string (Project -> Connect). Render needs IPv4, so use the pooler string if the direct one fails. Keep `?sslmode=require`.
2. In `.env` locally set `DATABASE_URL`, then run once: `python manage.py init-db`, `import-csv`, `create-editor NAME` (one per student), and optionally `enrich-posters`.
3. Push to GitHub (no `.env`). **Render:** New -> Blueprint (`render.yaml`). Set `DATABASE_URL`, `CORS_ORIGINS` (your frontend origins) and keep the generated `SECRET_KEY`.
4. Check `https://<service>.onrender.com/api/health`: `database: connected`, `movies: 4803`. Give that URL to your partner.
5. Test cross-app updates: edit a movie on one app, re-fetch on the other; post a rating from the partner app and open User Engagement.
Free Render services sleep when idle; open `/api/health` first.

## Backup and restore
- Fresh CSV: Data Management -> Download (or `GET /api/export/movies.csv`). The original CSVs remain your initial backup.
- Full backup (use the direct/session connection string in plain `postgresql://` form): `pg_dump "<URL>" --format=custom --file=movies_backup.dump`
- Restore into a NEW empty database: `pg_restore --no-owner --dbname="<NEW_URL>" movies_backup.dump`. Never restore over the live database without taking a fresh backup first. Supabase also offers dashboard backups depending on your plan.

## Tests
`python -m pytest -q` (temporary SQLite file; never touches `DATABASE_URL`). For PostgreSQL: create an empty database whose name ends in `_test` and run `TEST_DATABASE_URL=postgresql://user:pw@host/movies_test python -m pytest -q` (tables are dropped and recreated, so never use production).

## Faculty demo (about 7 minutes)
1. Overview: KPIs, charts, "Last updated"; change the period.
2. Movie Explorer: posters, filters, add two movies to Compare -> comparison page.
3. Financial Insights: formulas, ROI rule, unknown vs zero.
4. Log in as editor, edit a movie's rating; show the saved confirmation.
5. Partner app (or `/docs` / `partner_client.py`): fetch the same movie, see the new rating.
6. Partner posts a rating and a recommendation click -> User Engagement page.
7. Data Management: export CSV (contains the edit); show the row in Supabase's Table Editor.

## Known limitations
No live TMDB poster run yet; no genre radar/multi-genre comparison beyond the comparison table; "add movie" exists in `/docs` (POST) but not as a dashboard form; no email verification, password reset or login rate-limiting; no recommendation service is hosted here.

## Troubleshooting
`/api/health` `unavailable`: wrong `DATABASE_URL`/password or IPv6-only direct host. 503 "No movies": run `import-csv`. 401/403: log in again / use an editor account. Posters stay placeholders until `enrich-posters` has run. Charts blank offline: Chart.js loads from a CDN, tables and API still work.
