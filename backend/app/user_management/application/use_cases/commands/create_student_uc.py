from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.services.password_service import IPasswordService
from user_management.application.exceptions.exception import InvalidUserDataException,UserAlreadyExistsException,UserCreationFailedException
from user_management.application.services.jwt_service import IJWTService
from user_management.domain.events.user_events import StudentCreatedEvent
from user_management.application.services.send_mail_for_wlc_an_password_service import ISendMailForWlcAndPasswordService
from user_management.application.services.password_generator_service import IPasswordGeneratorService
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

    async def create_student(self, first_name: str, last_name: str, email: str, registration_number: str,establishment: str) -> str:
        # Validate input data
        if not all([first_name, last_name, email, registration_number, establishment]):
            raise InvalidUserDataException("All fields are required.")

        # Check if the student already exists
        if await self.student_repo.exists(registration_number):
            raise UserAlreadyExistsException(f"Student with registration number {registration_number} already exists.")
        password = self.password_generator_service.generate_password()
        hashed_password = self.password_service.hash_password(password)
        student=await self.student_repo.create_student(first_name, last_name, email, registration_number,establishment,hashed_password)
        if not student:
            raise UserCreationFailedException("Failed to create student.")
        #dispatch the created student event
        event = StudentCreatedEvent(student_id=student.student_id)
        await self.event_repo.dispatch(event)   
        # Send welcome email with the generated password
        await self.send_mail_service.send_welcome_email(email, password)
        # Generate JWT token for the newly created student
        token = self.jwt_service.generate_token(user_id=str(student.student_id), expires_delta=None)
        return token
        

        