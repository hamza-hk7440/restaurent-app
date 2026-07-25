from user_management.domain.interfaces.user_repo import IStudentRepository
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.services.password_service import IPasswordService
from user_management.application.services.ocr_service import IOCRService
from user_management.application.services.jwt_service import IJWTService
from user_management.application.exceptions.exception import (UserNotFoundException,OCRScanFailedException)
from user_management.application.dtos.student_dto import StudentDTO
class GetStudentInfoFromOCRUseCase:
    def __init__(
        self, 
        student_repo: IStudentRepository, 
        event_repo: IEventRepository, 
        password_service: IPasswordService, 
        ocr_service: IOCRService, 
        jwt_service: IJWTService,
        student_dto: StudentDTO

    ):
        self.student_repo = student_repo
        self.event_repo = event_repo
        self.password_service = password_service
        self.ocr_service = ocr_service
        self.jwt_service = jwt_service
        self.student_dto = student_dto

    async def execute(self, image_path: str)-> StudentDTO:
        registration_number = self.ocr_service.extract_student_id_from_card(image_path)
        if not registration_number:
            raise OCRScanFailedException("Failed to extract student ID from the provided image.")
        student = await self.student_repo.get_student_info_by_registration_number(registration_number)
        if not student:
            raise UserNotFoundException("No student found with the extracted registration number.")
        return self.student_dto.from_entity(student)