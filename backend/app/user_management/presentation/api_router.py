from fastapi import APIRouter
from user_management.presentation.routes.admin_routes import router as admin_router
from user_management.presentation.routes.verification_routes import router as verification_router
from user_management.presentation.routes.student_routes import student_router 
api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(verification_router)
api_router.include_router(student_router)