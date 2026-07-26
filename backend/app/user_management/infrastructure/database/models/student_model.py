from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid
from user_management.domain.value_objects.status import StudentStatus
from user_management.infrastructure.base import BaseModel

Base = declarative_base()

class StudentModel(Base, BaseModel):
    __tablename__ = "Students"

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

    def __repr__(self):
        return f"<StudentModel(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, registration_number={self.registration_number}, establishment={self.establishment}, status={self.status}, email_verified={self.email_verified}, email_verified_at={self.email_verified_at}, password_hash=****, balance={self.balance})>"