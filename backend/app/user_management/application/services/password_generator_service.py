from abc import ABC, abstractmethod

class IPasswordGeneratorService(ABC):
    @abstractmethod
    def generate_password(self) -> str:
        pass
