from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import DataFetchFailedException

class GetStudentsByEstablishmentUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_students_by_establishment(self, establishment_id: str) -> list:
        students = await self.user_repo.get_students_by_establishment(establishment_id)
        if students is None:
            raise DataFetchFailedException("Failed to fetch students.")
        return students
        