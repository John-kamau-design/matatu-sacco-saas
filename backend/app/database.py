import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# 1. Load our credentials from the backend/.env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is missing from your .env file!")

# 2. Create the async engine that Uvicorn was looking for
engine = create_async_engine(DATABASE_URL, echo=True)

# 3. Create a session factory for executing database operations
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 4. Base class for our tables configuration
Base = declarative_base()

# 5. Dependency helper to safely open/close database connections in our routes
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()