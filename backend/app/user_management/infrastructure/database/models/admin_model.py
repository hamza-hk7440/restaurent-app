from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from uuid import uuid4
from user_management.infrastructure.config.database import Base
Base=declarative_base()

class AdminModel(Base):
    __tablename__ = "Admins"
    admin_id=Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<AdminModel(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, is_super_admin={self.is_super_admin})>"