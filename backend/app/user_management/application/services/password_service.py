from abc import ABC, abstractmethod

class IPasswordService(ABC):
    @abstractmethod
    def hash_password(password: str) -> str:
        pass
    @abstractmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        pass