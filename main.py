"""Entry point.  Run:  uvicorn main:app --reload      or      python main.py"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from api import router
from interactions import router as interactions_router
from config import API_BASE_URL, CORS_ORIGINS
from database import SessionLocal, db_summary, engine
from frontend import render_page
from models import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("movie_analytics")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(engine)        # creates missing tables only (non-destructive)
        with SessionLocal() as s:
            n = db_summary(s)["movies"]
        log.info("Database connected. %d movies. %s", n, "" if n else "Run: python manage.py import-csv")
    except SQLAlchemyError:
        log.exception("Could not reach the database at startup (check DATABASE_URL)")
    yield


app = FastAPI(title="Movie Analytics Dashboard API", version="2.0", lifespan=lifespan,
              description="Shared movie API over a PostgreSQL database (TMDB 5000). Reads are public; "
                          "POST/PATCH/export need an editor token from /api/auth/login."
                          + (f" Deployed base URL: {API_BASE_URL}" if API_BASE_URL else ""))
# Bearer tokens (not cookies) are used, so a partner frontend on another origin can call this API.
@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError):
    """Any unexpected database failure becomes a clean 503 (details go to the log, not to the client)."""
    log.exception("Database error on %s", request.url.path)
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
app.include_router(interactions_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    return render_page()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
