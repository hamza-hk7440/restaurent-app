from abc import ABC, abstractmethod

class IUnbanStudentsAutomaticallyService(ABC):
    @abstractmethod
    async def unban_students_automatically(self) -> None:
        pass