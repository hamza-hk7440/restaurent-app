from user_management.application.use_cases.queries.get_student_by_email_uc import GetStudentByEmailUseCase
from user_management.application.use_cases.queries.get_student_info_by_name_uc import GetStudentInfoByNameUseCase
from user_management.application.use_cases.queries.get_student_info_by_registration_number_uc import GetStudentInfoByRegistrationNumberUseCase
from user_management.application.use_cases.queries.get_students_by_establishment_uc import GetStudentsByEstablishmentUseCase
from fastapi import HTTPException
import traceback

class SearchController:
    def __init__(self, get_student_by_email_uc: GetStudentByEmailUseCase, get_student_info_by_name_uc: GetStudentInfoByNameUseCase, get_student_info_by_registration_number_uc: GetStudentInfoByRegistrationNumberUseCase, get_students_by_establishment_uc: GetStudentsByEstablishmentUseCase):
        self.get_student_by_email_uc = get_student_by_email_uc
        self.get_student_info_by_name_uc = get_student_info_by_name_uc
        self.get_student_info_by_registration_number_uc = get_student_info_by_registration_number_uc
        self.get_students_by_establishment_uc = get_students_by_establishment_uc
    async def get_student_by_email(self, email: str):
        try:
            print(f"[debug][get_student_by_email][controller] request email={email}")
            student = await self.get_student_by_email_uc.get_student_by_email(email)
            print("[debug][get_student_by_email][controller] success")
            return student
        except Exception as e:
            print("[debug][get_student_by_email][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    async def get_student_info_by_name(self, first_name: str, last_name: str):
        try:
            print(f"[debug][get_student_info_by_name][controller] request first_name={first_name} last_name={last_name}")
            students = await self.get_student_info_by_name_uc.get_student_info_by_name(first_name, last_name)
            print("[debug][get_student_info_by_name][controller] success")
            return students
        except Exception as e:
            print("[debug][get_student_info_by_name][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    async def get_student_info_by_registration_number(self, registration_number: str):
        try:
            print(f"[debug][get_student_info_by_registration_number][controller] request registration_number={registration_number}")
            students = await self.get_student_info_by_registration_number_uc.get_student_info_by_registration_number(registration_number)
            print("[debug][get_student_info_by_registration_number][controller] success")
            return students
        except Exception as e:
            print("[debug][get_student_info_by_registration_number][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    async def get_students_by_establishment(self, establishment: str):
        try:
            print(f"[debug][get_students_by_establishment][controller] request establishment={establishment}")
            students = await self.get_students_by_establishment_uc.get_students_by_establishment(establishment)
            print("[debug][get_students_by_establishment][controller] success")
            return students
        except Exception as e:
            print("[debug][get_students_by_establishment][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
    