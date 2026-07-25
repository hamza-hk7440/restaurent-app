from abc import ABC, abstractmethod

class IOCRService(ABC):
    @abstractmethod
    def extract_student_id_from_card(self, image_path: str) -> str:
        pass