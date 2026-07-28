from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from uuid import uuid4
from user_management.domain.value_objects.token_type import TokenType
from user_management.infrastructure.config.database import Base

class TokenModel(Base):
    __tablename__ = "Tokens"
    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    token_type = Column(
        Enum(
            TokenType,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            name="tokentype",
        ),
        nullable=False,
    )
    token_value = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<TokenModel(id={self.token_id}, user_id={self.user_id}, token_type={self.token_type}, created_at={self.created_at}, expires_at={self.expires_at})>"
