from jose import jwt,JWTError
from datetime import datetime, timedelta,timezone
from user_management.infrastructure.config.settings import get_settings
from typing import Optional
import secrets
from user_management.application.services.jwt_service import IJWTService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from user_management.infrastructure.database.models.token_model import TokenModel
from user_management.domain.value_objects.token_type import TokenType
from uuid import UUID

class JWTRepository(IJWTService):
    def __init__(self, db: AsyncSession | None = None):
        self.settings = get_settings()
        self.db = db

    def generate_token(self, user_id: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": user_id, "exp": expire}
        token= jwt.encode(to_encode, self.settings.JWT_SECRET, algorithm=self.settings.JWT_ALGORITHM)
        return token

    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.settings.JWT_SECRET, algorithms=[self.settings.JWT_ALGORITHM])
            return payload.get("sub")
        except JWTError:
            return None
    async def verify_refresh_token(self, token: str) -> Optional[str]:
        return await self._verify_stored_token(token, TokenType.REFRESH)
    def generate_password_reset_token(self) -> str:
        return secrets.token_urlsafe(32)
    def generate_verification_token(self) -> str:
        return secrets.token_urlsafe(32)
    def is_token_expired(self, expires_at: datetime) -> bool:
        return datetime.now(timezone.utc) > expires_at
    async def save_token(self, user_id: str, token: str, expires_at: datetime, token_type: TokenType = TokenType.REFRESH) -> None:
        if self.db is None:
            return
        model = TokenModel(
            user_id=UUID(str(user_id)),
            token_type=token_type,
            token_value=token,
            expires_at=expires_at,
        )
        self.db.add(model)
        await self.db.commit()
    async def save_verification_token(self, user_id: str, token: str, expires_at: datetime, token_type: TokenType = TokenType.VERIFICATION) -> Optional[str]:
        if self.db is None:
            return None
        model = TokenModel(
            user_id=UUID(str(user_id)),
            token_type=token_type,
            token_value=token,
            expires_at=expires_at,
        )
        self.db.add(model)
        await self.db.commit()

    async def verify_verification_token(self, token: str) -> Optional[str]:
        return await self._verify_stored_token(token, TokenType.VERIFICATION)
        
    async def verify_password_reset_token(self, token: str) -> Optional[str]:
        return await self._verify_stored_token(token, TokenType.PASSWORD_RESET)

    async def delete_token(self, token: str) -> None:
        if self.db is None:
            return
        stmt = delete(TokenModel).where(TokenModel.token_value == token)
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_token_expiry_time(self):
        settings = get_settings()
        return datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)

    async def _verify_stored_token(self, token: str, token_type: TokenType) -> Optional[str]:
        if self.db is None:
            return None
        stmt = select(TokenModel).where(
            TokenModel.token_value == token,
            TokenModel.token_type == token_type,
        )
        result = await self.db.execute(stmt)
        stored = result.scalar_one_or_none()
        if not stored:
            return None
        if self.is_token_expired(stored.expires_at):
            await self.delete_token(token)
            return None
        return str(stored.user_id)
