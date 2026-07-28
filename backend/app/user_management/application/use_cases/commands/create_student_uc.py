from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.services.password_service import IPasswordService
from user_management.application.exceptions.exception import InvalidUserDataException, UserAlreadyExistsException, UserCreationFailedException
from user_management.application.services.jwt_service import IJWTService
from user_management.domain.events.user_events import StudentCreatedEvent
from user_management.application.services.send_mail_for_wlc_an_password_service import ISendMailForWlcAndPasswordService
from user_management.application.services.password_generator_service import IPasswordGeneratorService
import traceback
import re
from user_management.domain.value_objects.status import StudentStatus
from user_management.domain.value_objects.token_type import TokenType

class CreateStudentUseCase:
    def __init__(
        self, 
        student_repo: IUserRepository, 
        event_repo: IEventRepository, 
        password_service: IPasswordService, 
        jwt_service: IJWTService,
        send_mail_service: ISendMailForWlcAndPasswordService,
        password_generator_service: IPasswordGeneratorService,
    ):
        self.student_repo = student_repo
        self.event_repo = event_repo
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.send_mail_service = send_mail_service
        self.password_generator_service = password_generator_service

    async def create_student(self, first_name: str, last_name: str, email: str, registration_number: str, establishment: str) -> str:
        print(f"[debug][create_student][uc] start email={email} registration_number={registration_number}")

        if not all([first_name, last_name, email, registration_number, establishment]):
            print("[debug][create_student][uc] validation failed: missing field")
            raise InvalidUserDataException("All fields are required.")

        if not first_name.strip() or not last_name.strip():
            print("[debug][create_student][uc] validation failed: invalid name")
            raise InvalidUserDataException("First name and last name cannot be empty.")

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            print("[debug][create_student][uc] validation failed: invalid email format")
            raise InvalidUserDataException("Invalid email format.")

        if not re.match(r"^\d{6}$", registration_number):
            print("[debug][create_student][uc] validation failed: registration number must be 6 digits")
            raise InvalidUserDataException("Registration number must be exactly 6 digits.")

        print("[debug][create_student][uc] checking if student exists")
        try:
            student_exists = await self.student_repo.exists(registration_number)
        except Exception as e:
            print(f"[debug][create_student][uc] exists check failed: {e}")
            raise RuntimeError(f"create_student failed at exists check: {e}") from e

        if student_exists:
            print("[debug][create_student][uc] validation failed: student already exists")
            raise UserAlreadyExistsException(f"Student with registration number {registration_number} already exists.")

        print("[debug][create_student][uc] generating password")
        password = self.password_generator_service.generate_password()

        print("[debug][create_student][uc] hashing password")
        hashed_password = self.password_service.hash_password(password)

        print("[debug][create_student][uc] creating student record")
        try:
            student = await self.student_repo.create_student(
                first_name, last_name, email, registration_number, establishment, hashed_password, status=StudentStatus.INACTIVE
            )
        except Exception as e:
            print(f"[debug][create_student][uc] create_student repo failed: {e}")
            raise RuntimeError(f"create_student failed at database commit: {e}") from e

        if not student:
            print("[debug][create_student][uc] user repo returned no student")
            raise UserCreationFailedException("Failed to create student.")

        print(f"[debug][create_student][uc] student created id={student.student_id}")

        print("[debug][create_student][uc] dispatching event")
        try:
            event = StudentCreatedEvent(
                student_id=student.student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                establishment=establishment,
                registration_number=registration_number
            )
            await self.event_repo.dispatch(event)
        except Exception as e:
            print(f"[debug][create_student][uc] event dispatch failed: {e}")
            raise RuntimeError(f"create_student failed at event dispatch: {e}") from e

        print("[debug][create_student][uc] sending verification email")
        try:
            verification_token = await self.send_mail_service.send_verification_email(email)
            verification_expires_at = await self.jwt_service.get_token_expiry_time()
            await self.jwt_service.save_token(
                str(student.student_id),
                verification_token,
                verification_expires_at,
                token_type=TokenType.VERIFICATION
            )
        except Exception as e:
            print(f"[debug][create_student][uc] verification email failed: {e}")
            raise RuntimeError(f"create_student failed at verification email: {e}") from e

        print("[debug][create_student][uc] generating token")
        token = self.jwt_service.generate_token(user_id=str(student.student_id))
        expires_at = await self.jwt_service.get_token_expiry_time()
        await self.jwt_service.save_token(str(student.student_id), token, expires_at)
        print("[debug][create_student][uc] done")
        return token
