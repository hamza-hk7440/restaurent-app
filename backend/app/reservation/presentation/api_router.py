from fastapi import APIRouter
from reservation.presentation.routes.admin_routes import router as admin_router
from reservation.presentation.routes.catalog_routes import router as catalog_router
from reservation.presentation.routes.notification_routes import router as notification_router
from reservation.presentation.routes.reservation_routes import router as reservation_router

api_router = APIRouter()
api_router.include_router(catalog_router)
api_router.include_router(reservation_router)
api_router.include_router(notification_router)
api_router.include_router(admin_router)
