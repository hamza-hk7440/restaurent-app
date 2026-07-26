from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import DataFetchFailedException
class GetAllAdminsUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_all_admins(self):
        admins = await self.user_repo.get_all_admins()
        if admins is None:
            raise DataFetchFailedException("Failed to fetch admins.")
        return admins