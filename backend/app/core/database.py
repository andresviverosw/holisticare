import ssl
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


def async_engine_url(database_url: str) -> str:
    """
    Strip sslmode from async URLs — asyncpg negotiates TLS via connect_args, and
    combining ?sslmode=require with connect_args ssl=True breaks Render Postgres.
    """
    parsed = urlparse(database_url)
    if not parsed.query:
        return database_url
    filtered = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key != "sslmode"
    ]
    query = urlencode(filtered) if filtered else ""
    return urlunparse(parsed._replace(query=query))


def asyncpg_connect_args(*, requires_ssl: bool) -> dict:
    if not requires_ssl:
        return {}
    return {"ssl": ssl.create_default_context()}


settings = get_settings()

engine = create_async_engine(
    async_engine_url(settings.database_url),
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args=asyncpg_connect_args(requires_ssl=settings.postgres_requires_ssl),
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
