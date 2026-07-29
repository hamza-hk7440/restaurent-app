from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.events.user_events import BannedStudentEvent
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.application.exceptions.exception import UserNotFoundException,BanStudentFailedException
from user_management.application.dtos.punishment_dto import PunishmentDTO
class BanStudentUseCase:
    def __init__(self, user_repo: IUserRepository, events_repo: IEventRepository,
                 punishment_dto: PunishmentDTO):
        self.user_repo = user_repo
        self.events_repo = events_repo
        self.punishment_dto = punishment_dto

    async def ban_student(self,admin_id: str, student_id: str, reason: str, duration: int) -> None:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        
        updated_student = await self.user_repo.ban_student(student_id=student_id, reason=reason, admin_id=admin_id, period_of_ban=duration)
        if not updated_student:
            raise BanStudentFailedException("Failed to ban student.")
        event = BannedStudentEvent(user_id=student.student_id, reason=reason, period_of_ban=duration)
        await self.events_repo.dispatch(event)