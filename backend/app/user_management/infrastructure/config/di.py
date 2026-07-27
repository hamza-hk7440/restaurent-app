from user_management.infrastructure.config.database import DatabaseConfig
from user_management.infrastructure.database.repositories.user_repository import UserRepository
from user_management.infrastructure.external.forget_password_repository import ForgetPasswordRepository
from user_management.infrastructure.external.jwt_repository import JWTRepository 
from user_management.infrastructure.external.send_mail_repository import SendMailForWlcAndPasswordService
from user_management.infrastructure.external.password_generator_repository import PasswordGeneratorRepository
from user_management.infrastructure.external.ocr_repository import OCRRepository
from user_management.infrastructure.external.password_repository import PasswordRepository
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from user_management.infrastructure.config.database import get_db
class DependencyInjector:
    def __init__(self):
        self.database_config = DatabaseConfig()
        self.user_repository = UserRepository(self.database_config)
        self.jwt_repository = JWTRepository()
        self.send_mail_service = SendMailForWlcAndPasswordService()
        self.password_generator_service = PasswordGeneratorRepository()
        self.ocr_service = OCRRepository()
        self.password_repository = PasswordRepository()
        self.forget_password_service = ForgetPasswordRepository(
            user_repository=self.user_repository,
            jwt_repository=self.jwt_repository,
            send_mail_service=self.send_mail_service
        )
    @staticmethod
    def get_user_repository() -> UserRepository:
        db=DatabaseConfig.get_session()
        return UserRepository(db)
    @staticmethod
    def get_password_generator_service() -> PasswordGeneratorRepository:
        return PasswordGeneratorRepository()
    @staticmethod
    def get_ocr_service() -> OCRRepository:
        return OCRRepository()
    @staticmethod
    def get_password_repository() -> PasswordRepository:
        return PasswordRepository()
    @staticmethod
    def get_forget_password_service() -> ForgetPasswordRepository:
        db=DatabaseConfig.get_session()
        user_repository = UserRepository(db)
        jwt_repository = JWTRepository()
        send_mail_service = SendMailForWlcAndPasswordService()
        return ForgetPasswordRepository(
            user_repository=user_repository,
            jwt_repository=jwt_repository,
            send_mail_service=send_mail_service
        )
    @staticmethod
    def get_jwt_repository() -> JWTRepository:
        return JWTRepository()
    @staticmethod
    def get_send_mail_service() -> SendMailForWlcAndPasswordService:
        return SendMailForWlcAndPasswordService()
    @staticmethod
    async def get_database() -> AsyncGenerator[AsyncSession, None]:
        async for session in get_db():
            yield session