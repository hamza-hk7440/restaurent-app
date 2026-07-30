from fastapi import APIRouter, Depends, status
from user_management.presentation.dependencies import get_search_controller
from user_management.presentation.controllers.search_controller import SearchController

search_router = APIRouter(prefix="/search", tags=["Search"])

@search_router.get("/student-by-email", status_code=status.HTTP_200_OK)
async def get_student_by_email(
    email: str,
    search_controller: SearchController = Depends(get_search_controller)
):
    result = await search_controller.get_student_by_email(email)
    return {"student": result}
@search_router.get("/student-by-name", status_code=status.HTTP_200_OK)
async def get_student_by_name(
    first_name: str,
    last_name: str,
    search_controller: SearchController = Depends(get_search_controller)
):
    result = await search_controller.get_student_info_by_name(first_name, last_name)
    return {"students": result}
@search_router.get("/student-by-registration-number", status_code=status.HTTP_200_OK)
async def get_student_by_registration_number(
    registration_number: str,
    search_controller: SearchController = Depends(get_search_controller)
):
    result = await search_controller.get_student_info_by_registration_number(registration_number)
    return {"student": result}
@search_router.get("/students-by-establishment", status_code=status.HTTP_200_OK)
async def get_students_by_establishment(
    establishment: str,
    search_controller: SearchController = Depends(get_search_controller)
):
    result = await search_controller.get_students_by_establishment(establishment)
    return {"students": result}