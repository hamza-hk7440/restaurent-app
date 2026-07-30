from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.application.exceptions.exception import UserNotFoundException
from user_management.domain.interfaces.events_repo import IEventRepository
from user_management.domain.events.user_events import  StudentInfoEditedEvent

class EditStudentInfosUseCase:
    def __init__(self, user_repo: IUserRepository, events_repo: IEventRepository):
        self.user_repo = user_repo
        self.events_repo = events_repo

    async def edit_student_infos(self, student_id: str, new_first_name: str, new_last_name: str, registration_number: str, establishment: str) -> None:
        student = await self.user_repo.get_student_by_id(student_id)
        if not student:
            raise UserNotFoundException("Student not found.")
        await self.user_repo.edit_first_name(student_id=student_id, first_name=new_first_name) if new_first_name else student.first_name
        await self.user_repo.edit_last_name(student_id=student_id, last_name=new_last_name) if new_last_name else student.last_name
        await self.user_repo.edit_registration_number(student_id=student_id, registration_number=registration_number)
        await self.user_repo.edit_establishment(student_id=student_id, establishment=establishment)
        event = StudentInfoEditedEvent(user_id=student.student_id, new_first_name=new_first_name, new_last_name=new_last_name)
        await self.events_repo.dispatch(event)