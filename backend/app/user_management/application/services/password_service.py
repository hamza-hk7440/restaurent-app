from abc import ABC, abstractmethod

class IPasswordService(ABC):
    @abstractmethod
    def hash_password(password: str) -> str:
        pass
    @abstractmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        pass
    @abstractmethod
    def validate_password_strength(password: str) -> bool:
        pass