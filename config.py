"""Configuration. Secrets come from environment variables (or a local .env file that is never committed)."""
import logging
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _load_env_file(path: Path) -> None:
    """Tiny .env reader. Real environment variables always win (setdefault)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(BASE_DIR / ".env")


def _normalize_db_url(url: str) -> str:
    """Accept Supabase/Render style postgres:// URLs and select the psycopg2 driver."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


# Local development default: a SQLite file. Production/demo: your Supabase PostgreSQL URL.
DATABASE_URL = _normalize_db_url(os.environ.get("DATABASE_URL") or f"sqlite:///{(BASE_DIR / 'local_dev.db').as_posix()}")

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)   # fine for one local process; set SECRET_KEY on the server
    logging.getLogger("movie_analytics").warning("SECRET_KEY not set: using a random key (logins reset on restart).")
TOKEN_TTL_SECONDS = int(os.environ.get("TOKEN_TTL_SECONDS", 8 * 3600))
# Local SQLite dev: allow any origin. Hosted PostgreSQL: NO cross-origin access unless CORS_ORIGINS lists your frontends.
_default_cors = "*" if DATABASE_URL.startswith("sqlite") else ""
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", _default_cors).split(",") if o.strip()]
API_BASE_URL = os.environ.get("API_BASE_URL", "")   # documentation only: your deployed URL

DATA_DIR = BASE_DIR / "data"
MOVIES_CSV = DATA_DIR / "tmdb_5000_movies.csv"
CREDITS_CSV = DATA_DIR / "tmdb_5000_credits.csv"

DATASET_NAME = "TMDB 5000 Movie Dataset"
CURRENCY_NOTE = "USD, nominal values as recorded in the dataset"
DEFAULT_MIN_VOTES = 500
ROI_MIN_BUDGET = 1_000_000
MAX_LIMIT = 100
