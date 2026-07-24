from abc import ABC, abstractmethod
from user_management.domain.entities.student import Student
from user_management.domain.entities.admin import Admin
from user_management.domain.interfaces.base import IRepository

class IStudentRepository(IRepository[Student], ABC):
    @abstractmethod
    async def exists(self,entity_id: str) -> bool:
        pass
    @abstractmethod
    async def create_student(self, student: Student) -> None:
        pass
    @abstractmethod
    async def get_first_name(self, student_id: str) -> str:
        pass
    @abstractmethod
    async def get_last_name(self, student_id: str) -> str:
        pass
    @abstractmethod
    async def get_email(self, student_id: str) -> str:
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
    async def delete_student(self, student_id: str) -> None:
        pass
    @abstractmethod
    async def get_student_by_email(self, email: str) -> Student:
        pass
    @abstractmethod
    async def get_all_admins(self) -> list[Admin]:
        pass