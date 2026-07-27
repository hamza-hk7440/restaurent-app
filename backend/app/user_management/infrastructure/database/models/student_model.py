from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from uuid import uuid4
from user_management.domain.value_objects.status import StudentStatus

from user_management.infrastructure.config.database import Base
Base = declarative_base()

class StudentModel(Base, ):
    __tablename__ = "Students"
    student_id=Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    registration_number = Column(String(20), unique=True, nullable=False)
    establishment = Column(String(100), nullable=False)
    registration_number = Column(String(20), unique=True, nullable=False)
    status = Column(Enum(StudentStatus), default=StudentStatus.ACTIVE,nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    password_hash = Column(String(255), nullable=False)
    balance = Column(Integer, default=0, nullable=False)
    verification_token = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<StudentModel(id={self.student_id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, registration_number={self.registration_number}, establishment={self.establishment}, status={self.status}, email_verified={self.email_verified}, email_verified_at={self.email_verified_at}, password_hash=****, balance={self.balance})>"