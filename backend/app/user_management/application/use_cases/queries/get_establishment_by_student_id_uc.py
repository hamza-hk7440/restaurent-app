from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import DataFetchFailedException

class GetEstablishmentByStudentIdUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_establishment_by_student_id(self, student_id: str) -> dict:
        establishment_info = await self.user_repo.get_establishment_by_student_id(student_id)
        if establishment_info is None:
            raise DataFetchFailedException("Failed to fetch establishment info.")
        return establishment_info