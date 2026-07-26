from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import DataFetchFailedException

class GetEstablishmentByRegistrationNumberUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_establishment_by_registration_number(self, registration_number: str) -> dict:
        establishment_info = await self.user_repo.get_establishment_by_registration_number(registration_number)
        if establishment_info is None:
            raise DataFetchFailedException("Failed to fetch establishment info.")
        return establishment_info