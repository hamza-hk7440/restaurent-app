from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import PunishmentNotFoundException,PunishmentEditFailedException

class EditPunishmentPeriodUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def edit_punishment_period(self, punishment_id: str, new_period: int) -> None:
        punishment = await self.user_repo.get_punishment_by_id(punishment_id)
        if not punishment:
            raise PunishmentNotFoundException("Punishment not found.")
        
        updated_punishment = await self.user_repo.edit_punishment_period(punishment_id, new_period)
        if not updated_punishment:
            raise PunishmentEditFailedException("Failed to edit punishment period.")