from jose import jwt,JWTError
from datetime import datetime, timedelta,timezone
from user_management.infrastructure.config.settings import get_settings
from typing import Optional
import secrets
from user_management.application.services.jwt_service import IJWTService

class JWTRepository(IJWTService):
    def __init__(self):
        self.settings = get_settings()

    def generate_token(self, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": user_id, "exp": expire}
        token= jwt.encode(to_encode, self.settings.JWT_SECRET, algorithm=self.settings.JWT_ALGORITHM)
        return token

    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.settings.JWT_SECRET, algorithms=[self.settings.JWT_ALGORITHM])
            return payload.get("sub")
        except JWTError:
            return None
    def generate_password_reset_token()-> str:
        return secrets.token_urlsafe(32)
    def generate_verification_token()-> str:
        return secrets.token_urlsafe(32)
    def is_token_expired(self, expires_at: datetime) -> bool:
        return datetime.now(timezone.utc) > expires_at
    def save_token(self, token: str, expires_at: datetime) -> None:
        #in supabase
        pass
    def verify_verification_token(self, token: str) -> Optional[str]:
        #in supabase
        pass
        
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        #in supabase
        pass
    def delete_token(self, token: str) -> None:
        #in supabase
        pass
    async def get_token_expiry_time():
        settings = get_settings()
        return datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)