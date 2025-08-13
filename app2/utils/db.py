# app/utils/db.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import resolve_database_url

# Handle different database types for async connections
database_url = resolve_database_url()
if database_url.startswith("sqlite"):
    # Convert SQLite URL to use aiosqlite async driver
    DATABASE_URL = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif database_url.startswith("postgresql"):
    # Convert PostgreSQL URL to use asyncpg driver
    DATABASE_URL = database_url.replace("postgresql://", "postgresql+asyncpg://")
else:
    DATABASE_URL = database_url

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Declarative base for models
Base = declarative_base()

# Dependency for FastAPI routes
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session