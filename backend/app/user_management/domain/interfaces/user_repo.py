from abc import ABC, abstractmethod
from datetime import datetime
from user_management.domain.entities.student import Student
from user_management.domain.entities.admin import Admin
from user_management.domain.interfaces.base import IRepository
from user_management.domain.value_objects.status import StudentStatus
from user_management.domain.entities.punishment import Punishment
from user_management.domain.value_objects.status import StudentStatus
class IUserRepository(ABC):
    @abstractmethod
    async def exists(self,entity_id: str) -> bool:
        pass
    @abstractmethod
    async def create_student(self, student: Student) -> None:
        pass
    @abstractmethod
    async def get_registration_number_by_student_id(self, student_id: str) -> str:
        pass
    @abstractmethod
    async def get_registration_number_by_student_name(self, first_name: str, last_name: str) -> str:
        pass
    @abstractmethod
    async def get_registration_number_by_email(self, email: str) -> str:
        pass
    @abstractmethod
    async def get_establishment_by_student_id(self, student_id: str) -> str:
        pass
    @abstractmethod
    async def get_establishment_by_registration_number(self, registration_number: str) -> str:
        pass
    @abstractmethod
    async def edit_first_name(self, student_id: str, first_name: str) -> None:
        pass
    @abstractmethod
    async def edit_last_name(self, student_id: str, last_name: str) -> None:
        pass
    @abstractmethod
    async def edit_email(self, student_id: str, email: str) -> None:
        pass
    @abstractmethod
    async def change_password(self, student_id: str, password: str) -> None:
        pass
    @abstractmethod
    async def get_student_info_by_name(self, first_name: str, last_name: str) -> list[Student]:
        pass
    @abstractmethod
    async def get_student_info_by_registration_number(self, registration_number: str) -> list[Student]:
        pass
    @abstractmethod
    async def get_students_by_establishment(self, establishment: str) -> list[Student]:
        pass
    @abstractmethod
    async def get_all_students(self) -> list[Student]:
        pass
    @abstractmethod
    async def get_student_by_email(self, email: str) -> Student:
        pass
    @abstractmethod
    async def get_all_admins(self) -> list[Admin]:
        pass
    @abstractmethod
    async def get_student_by_id(self, student_id: str) -> Student:
        pass
    @abstractmethod
    async def get_student_status(self, student_id: str) -> StudentStatus:
        pass
    @abstractmethod
    async def get_punishments_by_student_id(self, student_id: str) -> list[Punishment]:
        pass
    @abstractmethod
    async def edit_student_status(self, student_id: str, status: StudentStatus) -> Student:
        pass
    @abstractmethod
    async def ban_student(self, punishment: Punishment) -> None:
        pass
    @abstractmethod
    async def unban_student(self, student_id: str) -> None:
        pass
    @abstractmethod
    async def edit_student_infos(self, student_id: str, first_name: str = None, last_name: str = None, email: str = None, establishment: str = None, email_verified: bool = None, email_verified_at: datetime = None,status: StudentStatus=None) -> None:
        pass
    @abstractmethod
    async def logout_user(self, student_id: str) -> None:
        pass
    @abstractmethod
    async def save_verification_token(self, student_id: str, token: str) -> None:
        pass
    @abstractmethod
    async def get_by_verification_token(self, token: str) -> Student:
        pass
    @abstractmethod
    async def mark_email_as_verified(self, student_id: str) -> None:
        pass
