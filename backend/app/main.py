from fastapi import FastAPI

from user_management.presentation.api_router import api_router
from user_management.infrastructure.config.database import DatabaseConfig

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await DatabaseConfig.init_db()
    yield

app=FastAPI(lifespan=lifespan)

app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}