from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import DataFetchFailedException

class GetAllStudentsUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_all_students(self):
        students = await self.user_repo.get_all_students()
        if students is None:
            raise DataFetchFailedException("Failed to fetch students.")
        return students