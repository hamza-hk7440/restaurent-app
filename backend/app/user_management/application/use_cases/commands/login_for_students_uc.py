from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.services.password_service import IPasswordService
from user_management.application.services.jwt_service import IJWTService
from user_management.application.exceptions.exception import (InvalidCredentialsException)

class LoginForStudentsUseCase:
    def __init__(
        self, 
        student_repo: IUserRepository, 
        event_repo: IEventRepository, 
        password_service: IPasswordService, 
        jwt_service: IJWTService
    ):
        self.student_repo = student_repo
        self.event_repo = event_repo
        self.password_service = password_service
        self.jwt_service = jwt_service

    async def normal_login(self, email: str, password: str) -> str:
        print(f"[debug][student_login][use_case] start email={email!r}")
        student = await self.student_repo.get_student_by_email(email) 
        print(f"[debug][student_login][use_case] student_found={bool(student)}")
        if not student:
            raise InvalidCredentialsException("Invalid email or password.")

        print(
            "[debug][student_login][use_case] "
            f"student_id={getattr(student, 'student_id', None)!r} "
            f"stored_email={getattr(student, 'email', None)!r} "
            f"password_type={type(getattr(student, 'password', None)).__name__} "
            f"password_len={len(getattr(student, 'password', '') or '')} "
            f"password_repr={getattr(student, 'password', None)!r}"
        )
        print(
            "[debug][student_login][use_case] "
            f"input_password_len={len(password or '')} "
            f"input_password_repr={password!r}"
        )
        is_valid = self.password_service.verify_password(password, student.password)
        print(f"[debug][student_login][use_case] password_valid={is_valid}")
        if not is_valid:
            raise InvalidCredentialsException("Invalid email or password.")

        token = self.jwt_service.generate_token(user_id=str(student.student_id))
        expires_at = await self.jwt_service.get_token_expiry_time()
        await self.jwt_service.save_token(str(student.student_id), token, expires_at)
        return token
