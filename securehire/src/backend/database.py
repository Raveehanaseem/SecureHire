"""
Database Configuration
SQLAlchemy async setup with PostgreSQL
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from collections.abc import AsyncGenerator 
import logging

from config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        from models import user, job, application  # noqa - import all models
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection for DB session with proper async context handling"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            
        except Exception as e:
            logger.error(f"Database transaction error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()