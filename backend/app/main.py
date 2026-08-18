from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from user_management.infrastructure.config.database import DatabaseConfig
from user_management.infrastructure.external.unban_students_automatically_repository import (
    UnbanStudentsAutomaticallyRepository,
)
from user_management.presentation.api_router import api_router
from reservation.presentation.api_router import api_router as reservation_router
from reservation.presentation.middleware.exception_handler import register_reservation_exception_handlers

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def unban_students_job():
    try:
        # Get session directly from DatabaseConfig
        session = await DatabaseConfig.get_session()
        async with session:
            await UnbanStudentsAutomaticallyRepository.unban_students_automatically(session)
            await session.commit()
            print("[Scheduler] Checked and auto-unbanned expired students.")
    except Exception as e:
        logger.error(f"[Scheduler Error] Failed to run unban_students_job: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB Engine and Session Factory
    await DatabaseConfig.init_db()
    await DatabaseConfig.create_all_tables()

    # 2. Start Background Scheduler
    scheduler.add_job(unban_students_job, "interval", minutes=2)
    scheduler.start()
    print("Scheduler started.")

    yield  # App is running and serving requests

    # 3. Cleanup on Shutdown
    scheduler.shutdown()
    print("Scheduler stopped.")
    await DatabaseConfig.close()
    print("Database connection closed.")


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
app.include_router(reservation_router)
register_reservation_exception_handlers(app)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}