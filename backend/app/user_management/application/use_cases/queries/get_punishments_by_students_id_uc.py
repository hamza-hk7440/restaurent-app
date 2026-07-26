from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import UserNotFoundException
from user_management.application.dtos.punishment_dto import PunishmentDTO
class GetPunishmentsByStudentIdUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_punishments_by_student_id(self, student_id: str) -> list[PunishmentDTO]:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        
        punishments = await self.user_repo.get_punishments_by_student_id(student_id)
        return [PunishmentDTO.from_entity(punishment) for punishment in punishments]