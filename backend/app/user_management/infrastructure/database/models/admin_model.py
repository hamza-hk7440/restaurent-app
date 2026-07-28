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
    username=Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password= Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AdminModel(id={self.id}, username={self.username}, email={self.email})>"