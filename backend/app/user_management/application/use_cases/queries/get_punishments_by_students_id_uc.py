from user_management.domain.interfaces.user_repo import IUserRepository
from uuid import UUID
from user_management.application.exceptions.exception import UserNotFoundException
from user_management.application.dtos.punishment_dto import PunishmentDTO
class GetPunishmentsByStudentIdUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_punishments(self, student_id: str) -> list[PunishmentDTO]:
        id=UUID(str(student_id))
        student = await self.user_repo.get_student_by_id(id)
        if not student:
            raise UserNotFoundException("Student not found.")
        
        punishments = await self.user_repo.get_punishments_by_student_id(student_id=id)
        return [PunishmentDTO.from_entity(punishment) for punishment in punishments]