import enum

class TokenType(enum.Enum):
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    REFRESH = "refresh"