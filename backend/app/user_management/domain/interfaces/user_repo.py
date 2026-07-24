from abc import ABC, abstractmethod
from user_management.domain.entities.user import User
from user_management.domain.interfaces.base import IRepository

class IUserRepository(IRepository[User], ABC):
    @abstractmethod
    async def exists(self,entity_id: str) -> bool:
        pass
    @abstractmethod
    async def create_student(self, student: User) -> None:
        pass
    @abstractmethod
    async def get_first_name(self, user_id: str) -> str:
        pass
    @abstractmethod
    async def get_last_name(self, user_id: str) -> str:
        pass
    @abstractmethod
    async def get_email(self, user_id: str) -> str:
        pass
    @abstractmethod
    async def get_registration_number_by_user_id(self, user_id: str) -> str:
        pass
    @abstractmethod
    async def get_registration_number_by_user_name(self, first_name: str, last_name: str) -> str:
        pass
    @abstractmethod
    async def get_registration_number_by_email(self, email: str) -> str:
        pass
    @abstractmethod
    async def get_establishment_by_user_id(self, user_id: str) -> str:
        pass
    @abstractmethod
    async def get_establishment_by_registration_number(self, registration_number: str) -> str:
        pass
    @abstractmethod
    async def edit_first_name(self, user_id: str, first_name: str) -> None:
        pass
    @abstractmethod
    async def edit_last_name(self, user_id: str, last_name: str) -> None:
        pass
    @abstractmethod
    async def edit_email(self, user_id: str, email: str) -> None:
        pass
    @abstractmethod
    async def change_password(self, user_id: str, password: str) -> None:
        pass
    @abstractmethod
    async def get_student_info_by_name(self, first_name: str, last_name: str) -> list[User]:
        pass
    @abstractmethod
    async def get_student_info_by_registration_number(self, registration_number: str) -> list[User]:
        pass
    @abstractmethod
    async def get_students_by_establishment(self, establishment: str) -> list[User]:
        pass
    @abstractmethod
    async def get_all_students(self) -> list[User]:
        pass
    @abstractmethod
    async def delete_student(self, user_id: str) -> None:
        pass
    @abstractmethod
    async def get_student_by_email(self, email: str) -> User:
        pass