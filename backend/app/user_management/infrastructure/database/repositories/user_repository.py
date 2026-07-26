from operator import and_
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from user_management.infrastructure.database.models.student_model import StudentModel
from user_management.infrastructure.database.repositories.base_repository import BaseRepository
from user_management.domain.value_objects.status import StudentStatus
from user_management.domain.entities.student import Student
from user_management.domain.entities.admin import Admin
from user_management.domain.interfaces.user_repo import IUserRepository
from user_management.domain.entities.punishment import Punishment
from user_management.infrastructure.database.models.punishment_model import PunishmentModel
from user_management.infrastructure.database.models.admin_model import AdminModel
from uuid import UUID
class StudentRepository(BaseRepository[StudentModel],BaseRepository[AdminModel],BaseRepository[PunishmentModel], IUserRepository):
    def __init__(self, db_session: Session):
       
        self.db = db_session
    
    
    async def exists(self, entity_id: str) -> bool:
       
        try:
            student_uuid = UUID(entity_id)
        except ValueError:
            return False
        
        return self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first() is not None

    
    async def create_student(self, student: Student) -> None:
        
        student_model = StudentModel(
            id=student.student_id,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            password=student.password,
            establishment=student.establishment,
            registration_number=student.registration_number,
            status=student.status,
            email_verified=student.email_verified,
            email_verified_at=student.email_verified_at,
            is_admin_created=student.is_admin_created,
            must_change_password=student.must_change_password,
            password_created_at=student.password_created_at,
            temporary_password_expires=student.temporary_password_expires,
            balance_cents=student.balance_cents,
            is_active=student.is_active
        )
        
        self.db.add(student_model)
        self.db.commit()

    
    async def get_registration_number_by_student_id(self, student_id: str) -> str:
       
        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return None
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        return student.registration_number if student else None
    
    async def get_registration_number_by_student_name(self, first_name: str, last_name: str) -> str:
        student = self.db.query(StudentModel).filter(
            and_(
                StudentModel.first_name == first_name,
                StudentModel.last_name == last_name
            )
        ).first()
        
        return student.registration_number if student else None
    
    async def get_registration_number_by_email(self, email: str) -> str:
        student = self.db.query(StudentModel).filter(
            StudentModel.email == email.lower()
        ).first()
        
        return student.registration_number if student else None
   
    async def get_establishment_by_student_id(self, student_id: str) -> str:
        
        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return None
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        return student.establishment if student else None
    
    async def get_establishment_by_registration_number(self, registration_number: str) -> str:
       
        student = self.db.query(StudentModel).filter(
            StudentModel.registration_number == registration_number
        ).first()
        
        return student.establishment if student else None
    
   
    async def edit_first_name(self, student_id: str, first_name: str) -> None:
       
        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        if student:
            student.first_name = first_name
            student.updated_at = datetime.utcnow()
            self.db.commit()
    
    async def edit_last_name(self, student_id: str, last_name: str) -> None:
       
        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        if student:
            student.last_name = last_name
            student.updated_at = datetime.utcnow()
            self.db.commit()
    
    async def edit_email(self, student_id: str, email: str) -> None:

        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        if student:
            student.email = email.lower()
            student.email_verified = False
            student.email_verified_at = None
            student.updated_at = datetime.utcnow()
            self.db.commit()
    
    async def change_password(self, student_id: str, password: str) -> None:

        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        if student:
            student.password = password
            student.must_change_password = False
            student.updated_at = datetime.utcnow()
            self.db.commit()
    
    async def edit_student_infos(
        self,
        student_id: str,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        establishment: str = None,
        email_verified: bool = None,
        email_verified_at: datetime = None
    ) -> None:

        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
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
        
        if email_verified is not None:
            student.email_verified = email_verified
        
        if email_verified_at is not None:
            student.email_verified_at = email_verified_at
        
        student.updated_at = datetime.utcnow()
        self.db.commit()

    
    async def get_student_by_id(self, student_id: str) -> Optional[Student]:

        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return None
        
        model = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        return self._map_to_entity(model) if model else None
    
    async def get_student_by_email(self, email: str) -> Optional[Student]:
 
        model = self.db.query(StudentModel).filter(
            StudentModel.email == email.lower()
        ).first()
        
        return self._map_to_entity(model) if model else None 
    async def get_student_info_by_name(self, first_name: str, last_name: str) -> List[Student]:

        models = self.db.query(StudentModel).filter(
            and_(
                StudentModel.first_name == first_name,
                StudentModel.last_name == last_name
            )
        ).all()
        
        return [self._map_to_entity(model) for model in models]
    
    async def get_student_info_by_registration_number(self, registration_number: str) -> List[Student]:

        models = self.db.query(StudentModel).filter(
            StudentModel.registration_number == registration_number
        ).all()
        
        return [self._map_to_entity(model) for model in models]
    
    async def get_students_by_establishment(self, establishment: str) -> List[Student]:

        models = self.db.query(StudentModel).filter(
            StudentModel.establishment == establishment
        ).all()
        
        return [self._map_to_entity(model) for model in models]
    
    async def get_all_students(self) -> List[Student]:

        models = self.db.query(StudentModel).filter(
            StudentModel.is_active == True
        ).all()
        
        return [self._map_to_entity(model) for model in models]
    
 
    async def get_student_status(self, student_id: str) -> Optional[StudentStatus]:
      
        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return None
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        return student.status if student else None
    
    async def edit_student_status(self, student_id: str, status: StudentStatus) -> Student:
       
        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return None
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        if student:
            student.status = status
            # Auto-disable if banned
            if status == StudentStatus.BANNED:
                student.is_active = False
            elif status == StudentStatus.ACTIVE:
                student.is_active = True
            
            student.updated_at = datetime.utcnow()
            self.db.commit()
            
            return self._map_to_entity(student)
        
        return None
    
    
    async def get_punishments_by_student_id(self, student_id: str) -> List[Punishment]:
       
        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return []
        
        punishments = self.db.query(PunishmentModel).filter(
            PunishmentModel.student_id == student_uuid
        ).all()
        
        return [self._map_punishment_to_entity(p) for p in punishments]
    
    async def ban_student(self, punishment: Punishment) -> None:
       
        punishment_model = PunishmentModel(
            id=punishment.punishment_id,
            student_id=punishment.student_id,
            reason=punishment.reason,
            created_at=punishment.created_at
        )
        
        self.db.add(punishment_model)
        
        # Update student status
        student = self.db.query(StudentModel).filter(
            StudentModel.id == punishment.student_id
        ).first()
        
        if student:
            student.status = StudentStatus.BANNED
            student.is_active = False
            student.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    async def unban_student(self, student_id: str) -> None:
       
        try:
            student_uuid = UUID(student_id)
        except ValueError:
            return
        
        student = self.db.query(StudentModel).filter(
            StudentModel.id == student_uuid
        ).first()
        
        if student:
            student.status = StudentStatus.ACTIVE
            student.is_active = True
            student.updated_at = datetime.utcnow()
            self.db.commit()
    
   
    async def get_all_admins(self) -> List[Admin]:
       
        models = self.db.query(AdminModel).all()
        
        return [self._map_admin_to_entity(model) for model in models]

    
    async def logout_user(self, student_id: str) -> None:
       
        pass
    
    # ============================================
    # PRIVATE HELPER METHODS
    # ============================================
    
    def _map_to_entity(self, model: StudentModel) -> Optional[Student]:
       
        if not model:
            return None
        
        return Student(
            student_id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            password=model.password,
            created_at=model.created_at,
            updated_at=model.updated_at,
            establishment=model.establishment,
            registration_number=model.registration_number,
            status=model.status,
            email_verified=model.email_verified,
            email_verified_at=model.email_verified_at,
            is_admin_created=model.is_admin_created,
            must_change_password=model.must_change_password,
            password_created_at=model.password_created_at,
            temporary_password_expires=model.temporary_password_expires,
            balance_cents=model.balance_cents,
            is_active=model.is_active
        )
    
    def _map_admin_to_entity(self, model: AdminModel) -> Optional[Admin]:
       
        return Admin(
            admin_id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _map_punishment_to_entity(self, model: PunishmentModel) -> Optional[Punishment]:
        
        if not model:
            return None
        
        return Punishment(
            punishment_id=model.id,
            student_id=model.student_id,
            reason=model.reason,
            created_at=model.created_at
        )
 