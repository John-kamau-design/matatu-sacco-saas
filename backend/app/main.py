from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app import models
from app.routes import router as api_router

# 1. Modern Lifespan Manager for Database Initializations
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("🚀 Database tables verified and online via Lifespan!")
    yield

# 2. Initialize App with Lifespan
app = FastAPI(title="Matatu SaaS Core Engine", lifespan=lifespan)

# 3. Include Routers
app.include_router(api_router)

@app.get("/")
def home():
    return {"status": "online", "system": "Matatu SaaS MVP"}