from operator import and_
from typing import List, Optional
from unittest import result
from datetime import datetime, timezone, timedelta
from user_management.domain.value_objects.token_type import TokenType
from user_management.infrastructure.external.jwt_repository import JWTRepository
from user_management.infrastructure.database.models import student_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from user_management.infrastructure.config.settings import get_settings
from user_management.application.services.jwt_service import IJWTService
from datetime import datetime, timezone
from user_management.infrastructure.database.models.student_model import StudentModel
from user_management.infrastructure.database.repositories.base_repository import BaseRepository
from user_management.domain.value_objects.status import StudentStatus
from user_management.domain.entities.student import Student
from user_management.domain.entities.admin import Admin
from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.entities.punishment import Punishment
from user_management.infrastructure.database.models.punishment_model import PunishmentModel
from user_management.infrastructure.database.models.admin_model import AdminModel
from uuid import UUID, uuid4, uuid4

class UserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.settings = get_settings()
        self.jwt_service: IJWTService = JWTRepository(db_session)  # Initialize JWTRepository with the same session

    def _normalize_uuid(self, value):
        if isinstance(value, UUID):
            return value
        return UUID(str(value))
    
    async def exists(self, registration_number: str) -> bool:
        print(f"[debug][user_repo.exists] checking registration_number={registration_number}")        
        result = await self.db.execute(
            select(StudentModel.student_id).filter(
                StudentModel.registration_number == registration_number
            )
        )
        found = result.first() is not None
        print(f"[debug][user_repo.exists] found={found}")
        return found

    async def create_student(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        registration_number: str = None,
        establishment: str = None,
        hashed_password: str = None,
        status: StudentStatus = StudentStatus.ACTIVE,
        **kwargs
    ) -> StudentModel:
        if "student" in kwargs and kwargs["student"] is not None:
            student = kwargs["student"]
            first_name = getattr(student, "first_name", first_name)
            last_name = getattr(student, "last_name", last_name)
            email = getattr(student, "email", email)
            registration_number = getattr(student, "registration_number", registration_number)
            establishment = getattr(student, "establishment", establishment)
            hashed_password = getattr(student, "password", hashed_password)
            status = getattr(student, "status", status)

        print(f"[debug][user_repo.create_student] start email={email} registration_number={registration_number} status={status}")
        student_model = StudentModel(
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            registration_number=registration_number,
            establishment=establishment,
            password_hash=hashed_password,
            status=status
        )
        
        # ASYNC operations:
        print("[debug][user_repo.create_student] adding model")
        self.db.add(student_model)  
        print("[debug][user_repo.create_student] committing")
        await self.db.commit()      
        print("[debug][user_repo.create_student] refreshing")
        await self.db.refresh(student_model)  
        print(f"[debug][user_repo.create_student] done id={student_model.student_id}")        
        return student_model

    async def get_registration_number_by_student_id(self, student_id: str) -> str:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return None
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.id == student_uuid)
        )
        student = result.scalars().first()
        
        return student.registration_number if student else None
    
    async def get_registration_number_by_student_name(self, first_name: str, last_name: str) -> str:
        result = await self.db.execute(
            select(StudentModel).filter(
                and_(
                    StudentModel.first_name == first_name,
                    StudentModel.last_name == last_name
                )
            )
        )
        student = result.scalars().first()
        
        return student.registration_number if student else None
    
    async def get_registration_number_by_email(self, email: str) -> str:
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.email == email.lower())
        )
        student = result.scalars().first()
        
        return student.registration_number if student else None
   
    async def get_establishment_by_student_id(self, student_id: str) -> str:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return None
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.id == student_uuid)
        )
        student = result.scalars().first()
        
        return student.establishment if student else None
    
    async def get_establishment_by_registration_number(self, registration_number: str) -> str:
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.registration_number == registration_number)
        )
        student = result.scalars().first()
        
        return student.establishment if student else None
   
    async def edit_first_name(self, student_id: str, first_name: str) -> None:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        student = result.scalars().first()
        
        if student:
            student.first_name = first_name
            student.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
    
    async def edit_last_name(self, student_id: str, last_name: str) -> None:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        student = result.scalars().first()
        
        if student:
            student.last_name = last_name
            student.updated_at = datetime.utcnow()
            await self.db.commit()
    
    async def edit_email(self, student_id: str, email: str, verification_token: str) -> Optional[str]:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return None
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        student = result.scalars().first()
        if student:
            student.email = email.lower()
            await self.jwt_service.save_verification_token(student_id, verification_token, datetime.now(timezone.utc) + timedelta(hours=self.settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS), token_type=TokenType.VERIFICATION)
            student.email_verified = False                  # Reset verification state
            student.email_verified_at = None                 # Clear previous verification date
            student.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            return student.email
        
        return None
    
    async def change_password(self, student_id, new_password_hash: str) -> str:
        db_student = await self.db.get(StudentModel, self._normalize_uuid(student_id))
        if db_student:
            db_student.password_hash = new_password_hash
            await self.db.commit()
        return new_password_hash
    
    async def edit_student_infos(
        self,
        student_id: str,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        establishment: str = None,
        status: StudentStatus = None,
        email_verified: bool = None,
        email_verified_at: datetime = None
    ) -> None:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        student = result.scalars().first()
        
        if not student:
            return
        
        if first_name is not None:
            student.first_name = first_name
        
        if last_name is not None:
            student.last_name = last_name
        
        if email is not None:
            student.email = email.lower()
        
        if establishment is not None:
            student.establishment = establishment

        if status is not None:
            student.status = status
            student.is_active = status != StudentStatus.BANNED

        if email_verified is not None:
            student.email_verified = email_verified
        
        if email_verified_at is not None:
            student.email_verified_at = email_verified_at
        
        student.updated_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def get_student_by_id(self, student_id: str) -> Optional[Student]:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return None
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        model = result.scalars().first()
        
        return self._map_to_entity(model) if model else None
    
    async def get_student_by_email(self, email: str) -> Optional[Student]:
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.email == email.lower())
        )
        model = result.scalars().first()
        
        return self._map_to_entity(model) if model else None 

    async def get_student_info_by_name(self, first_name: str, last_name: str) -> List[Student]:
        result = await self.db.execute(
            select(StudentModel).filter(
                and_(
                    StudentModel.first_name == first_name,
                    StudentModel.last_name == last_name
                )
            )
        )
        models = result.scalars().all()
        
        return [self._map_to_entity(model) for model in models]
    
    async def get_student_info_by_registration_number(self, registration_number: str) -> List[Student]:
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.registration_number == registration_number)
        )
        models = result.scalars().all()
        
        return [self._map_to_entity(model) for model in models]
    
    async def get_students_by_establishment(self, establishment: str) -> List[Student]:
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.establishment == establishment)
        )
        models = result.scalars().all()
        
        return [self._map_to_entity(model) for model in models]
    
    async def get_all_students(self) -> List[Student]:
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.status == StudentStatus.ACTIVE)
        )
        models = result.scalars().all()
        
        return [self._map_to_entity(model) for model in models]
    
    async def get_student_status(self, student_id: str) -> Optional[StudentStatus]:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return None
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.id == student_uuid)
        )
        student = result.scalars().first()
        
        return student.status if student else None
    
    async def edit_student_status(self, student_id: str, status: StudentStatus) -> Student:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return None
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        student = result.scalars().first()
        
        if student:
            student.status = status
            if status == StudentStatus.BANNED:
                student.is_active = False
            elif status == StudentStatus.ACTIVE:
                student.is_active = True
            
            student.updated_at = datetime.utcnow()
            await self.db.commit()
            
            return self._map_to_entity(student)
        
        return None
    
    async def get_punishments_by_student_id(self, student_id: str) -> List[Punishment]:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return []
        
        result = await self.db.execute(
            select(PunishmentModel).filter(PunishmentModel.student_id == student_uuid)
        )
        punishments = result.scalars().all()
        
        return [self._map_punishment_to_entity(p) for p in punishments]
    
    async def ban_student(self, student_id: str, reason: str, admin_id: str, period_of_ban: int) -> None:
        punishment_model = PunishmentModel(
            punishment_id=str(uuid4()),
            student_id=student_id,
            reason=reason,
            admin_id=admin_id,
            period_of_ban=period_of_ban,
            created_at=datetime.utcnow()
        )
        
        self.db.add(punishment_model)
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_id)
        )
        student = result.scalars().first()
        
        if student:
            student.status = StudentStatus.BANNED
            student.is_active = False
            student.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return {f"Student {student_id} has been banned for {period_of_ban} days."}
    
    async def unban_student(self, student_id: str) -> str:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        student = result.scalars().first()
        
        if student:
            student.status = StudentStatus.ACTIVE
            student.is_active = True
            student.updated_at = datetime.utcnow()
            await self.db.commit()
        return f"Student {student_id} has been unbanned."
    
    async def get_all_admins(self) -> List[Admin]:
        result = await self.db.execute(select(AdminModel))
        models = result.scalars().all()
        
        return [self._map_admin_to_entity(model) for model in models]
    
    async def logout_user(self, student_id: str) -> None:
        pass

    async def save_verification_token(self, student_id: str, token: str) -> None:
        # Verification tokens now live in the Tokens table and are handled by JWTRepository.
        return None

    async def get_by_verification_token(self, token: str):
        # Deprecated compatibility shim.
        return None
    
    def _map_to_entity(self, model: StudentModel) -> Optional[Student]:
        if not model:
            return None
        
        return Student(
            student_id=model.student_id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            registration_number=model.registration_number,
            establishment=model.establishment,
            status=model.status,
            email_verified=model.email_verified,
            email_verified_at=model.email_verified_at,
            password=model.password_hash,
            balance=model.balance,
            created_at=model.created_at,
            updated_at=model.updated_at
            
        )
    
    def _map_admin_to_entity(self, model: AdminModel) -> Optional[Admin]:
        return Admin(
            admin_id=model.admin_id,
            email=model.email,
            username=model.username,
            created_at=model.created_at,
            password=model.password
        )
    
    def _map_punishment_to_entity(self, model: PunishmentModel) -> Optional[Punishment]:
        if not model:
            return None
        
        return Punishment(
            punishment_id=model.punishment_id,
            admin_id=model.admin_id,
            period_of_ban=model.period_of_ban,
            student_id=model.student_id,
            reason=model.reason,
            created_at=model.created_at
        )
    async def mark_email_as_verified(self, student_id: str) -> None:
        db_student = await self.db.get(StudentModel, self._normalize_uuid(student_id))
        if db_student:
            db_student.email_verified = True
            db_student.email_verified_at = datetime.now(timezone.utc)
            await self.db.commit()
    async def get_admin_by_email(self, email: str) -> Optional[Admin]:
        result = await self.db.execute(
            select(AdminModel).filter(AdminModel.email == email.lower())
        )
        model = result.scalars().first()
        
        return self._map_admin_to_entity(model) if model else None
    async def edit_registration_number(self, student_id: str, registration_number: str) -> None:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        student = result.scalars().first()
        
        if student:
            student.registration_number = registration_number
            student.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
    async def edit_establishment(self, student_id: str, establishment: str) -> None:
        try:
            student_uuid = self._normalize_uuid(student_id)
        except ValueError:
            return
        
        result = await self.db.execute(
            select(StudentModel).filter(StudentModel.student_id == student_uuid)
        )
        student = result.scalars().first()
        
        if student:
            student.establishment = establishment
            student.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
    async def edit_punishment_period(self, punishment_id: str, new_period: int) -> str:
        try:
            punishment_uuid = self._normalize_uuid(punishment_id)
        except ValueError:
            return
        
        result = await self.db.execute(
            select(PunishmentModel).filter(PunishmentModel.punishment_id == punishment_uuid)
        )
        punishment = result.scalars().first()
        
        if punishment:
            punishment.period_of_ban = new_period
            await self.db.commit()
        return f"Punishment {punishment_id} period updated to {new_period} minutes."
    async def get_punishment_by_id(self, punishment_id: str) -> Optional[Punishment]:
        try:
            punishment_uuid = self._normalize_uuid(punishment_id)
        except ValueError:
            return None
        
        result = await self.db.execute(
            select(PunishmentModel).filter(PunishmentModel.punishment_id == punishment_uuid)
        )
        model = result.scalars().first()
        
        return self._map_punishment_to_entity(model) if model else None
