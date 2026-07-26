from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid
from user_management.infrastructure.base import BaseModel

Base=declarative_base()

class AdminModel(Base, BaseModel):
    __tablename__ = "Admins"

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<AdminModel(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, is_super_admin={self.is_super_admin})>"