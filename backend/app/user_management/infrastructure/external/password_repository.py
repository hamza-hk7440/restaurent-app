from bcrypt import hashpw, gensalt, checkpw
import re
from user_management.application.services.password_service import IPasswordService

class PasswordRepository(IPasswordService):
    @staticmethod
    def hash_password(password: str) -> str:
        salt=gensalt(rounds=12)
        hashed_password = hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        # Password strength criteria:
        # At least 8 characters long
        # Contains at least one uppercase letter
        # Contains at least one lowercase letter
        # Contains at least one digit
        # Contains at least one special character
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True