from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from uuid import uuid4
from user_management.infrastructure.config.database import Base

class PunishmentModel(Base):
    __tablename__ = "Punishments"
    punishment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(UUID(as_uuid=True), nullable=False)
    admin_id = Column(UUID(as_uuid=True), nullable=False)
    reason = Column(String(255), nullable=False)
    period_of_ban = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<PunishmentModel(id={self.id}, student_id={self.student_id}, admin_id={self.admin_id}, reason={self.reason}, period_of_ban={self.period_of_ban})>"