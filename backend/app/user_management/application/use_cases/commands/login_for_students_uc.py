from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.services.password_service import IPasswordService
from user_management.application.services.ocr_service import IOCRService
from user_management.application.services.jwt_service import IJWTService
from user_management.application.exceptions.exception import (InvalidCredentialsException)

class LoginForStudentsUseCase:
    def __init__(
        self, 
        student_repo: IUserRepository, 
        event_repo: IEventRepository, 
        password_service: IPasswordService, 
        ocr_service: IOCRService, 
        jwt_service: IJWTService
    ):
        self.student_repo = student_repo
        self.event_repo = event_repo
        self.password_service = password_service
        self.ocr_service = ocr_service
        self.jwt_service = jwt_service

    async def normal_login(self, email: str, password: str) -> str:
        student = await self.student_repo.get_student_by_email(email) 
        if not student:
            raise InvalidCredentialsException("Invalid email or password.")

        is_valid = self.password_service.verify_password(password, student.password)
        if not is_valid:
            raise InvalidCredentialsException("Invalid email or password.")

        token = self.jwt_service.generate_token(user_id=str(student.student_id), expires_delta=None)
        return token
    async def ocr_login(self, registration_number: str,email: str ) -> str:
        student=await self.student_repo.get_student_info_by_registration_number(registration_number)
        if not student or student.email != email:
            raise InvalidCredentialsException("Invalid registration number or email.")
        token = self.jwt_service.generate_token(user_id=str(student.student_id), expires_delta=None)
        return token