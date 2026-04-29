import os

from dotenv import load_dotenv


def init_config() -> None:
    load_dotenv()


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        msg = "DATABASE_URL is not set"
        raise RuntimeError(msg)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def get_short_link_base() -> str:
    base = os.environ.get("SHORT_LINK_BASE", "").strip().rstrip("/")
    if not base:
        msg = "SHORT_LINK_BASE is not set"
        raise RuntimeError(msg)
    return base
