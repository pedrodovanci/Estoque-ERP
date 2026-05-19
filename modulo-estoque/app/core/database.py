from urllib.parse import quote

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


def normalize_database_url(raw_url: str) -> str:
    if not raw_url:
        return raw_url

    if raw_url.startswith("postgresql") and "://" in raw_url and "@" in raw_url:
        prefix, rest = raw_url.split("://", 1)
        userinfo, hostpart = rest.rsplit("@", 1)
        if ":" in userinfo:
            username, password = userinfo.split(":", 1)
            encoded_password = quote(password, safe="%")
            raw_url = f"{prefix}://{username}:{encoded_password}@{hostpart}"

    if ".supabase.co" in raw_url and "sslmode=" not in raw_url:
        raw_url = f"{raw_url}{'&' if '?' in raw_url else '?'}sslmode=require"

    return raw_url


engine = create_engine(normalize_database_url(settings.DATABASE_URL), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
