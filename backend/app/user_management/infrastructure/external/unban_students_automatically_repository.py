from user_management.application.services.unban_students_automatically_service import IUnbanStudentsAutomaticallyService
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update, join
from user_management.domain.value_objects.status import StudentStatus
from user_management.infrastructure.database.models.student_model import StudentModel
from user_management.infrastructure.database.models.punishment_model import PunishmentModel 
class UnbanStudentsAutomaticallyRepository(IUnbanStudentsAutomaticallyService):
    @staticmethod
    async def unban_students_automatically(db_session) ->int :
        now=datetime.now(timezone.utc)

        stmt=(
            update(StudentModel)
            .where(StudentModel.status==StudentStatus.BANNED)
            .where(
                StudentModel.student_id.in_(
                    select(PunishmentModel.student_id)
                    .where(PunishmentModel.created_at+PunishmentModel.period_of_ban*timedelta(minutes=1)<=now)
                )
            )
            .values(status=StudentStatus.ACTIVE,updated_at=now)
        )
        result=await db_session.execute(stmt)
        await db_session.commit()
        return result.rowcount
