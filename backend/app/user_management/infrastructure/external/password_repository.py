from bcrypt import hashpw, gensalt, checkpw
import re
from user_management.application.services.password_service import IPasswordService

class PasswordRepository(IPasswordService):
    @staticmethod
    def hash_password(password: str) -> str:
        normalized_password = password.strip()
        salt = gensalt(rounds=12)
        hashed_password = hashpw(normalized_password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if plain_password is None or hashed_password is None:
            return False

        normalized_password = plain_password.strip()
        normalized_hash = hashed_password.strip()

        if isinstance(normalized_hash, bytes):
            hashed_bytes = normalized_hash
        else:
            hashed_bytes = normalized_hash.encode("utf-8")

        if isinstance(normalized_password, bytes):
            password_bytes = normalized_password
        else:
            password_bytes = normalized_password.encode("utf-8")

        try:
            return checkpw(password_bytes, hashed_bytes)
        except ValueError:
            return False

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
