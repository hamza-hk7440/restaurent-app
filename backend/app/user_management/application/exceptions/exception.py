class UserManagementException(Exception):
    """Base class for all user management exceptions."""
    def __init__(self, message: str, error_code: str = "USER_MANAGEMENT_EXCEPTION"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
class UserNotFoundException(UserManagementException):
    """Exception raised when a user is not found."""
    def __init__(self, message: str = "User not found", error_code: str = "USER_NOT_FOUND"):
        super().__init__(message, error_code)
class InvalidUserDataException(UserManagementException):
    """Exception raised when user data is invalid."""
    def __init__(self, message: str = "Invalid user data", error_code: str = "INVALID_USER_DATA"):
        super().__init__(message, error_code)
class UnauthorizedUserException(UserManagementException):
    """Exception raised when a user is unauthorized to perform an action."""
    def __init__(self, message: str = "Unauthorized user", error_code: str = "UNAUTHORIZED_USER"):
        super().__init__(message, error_code)
class UserAlreadyExistsException(UserManagementException):
    """Exception raised when a user already exists."""
    def __init__(self, message: str = "User already exists", error_code: str = "USER_ALREADY_EXISTS"):
        super().__init__(message, error_code)
class UserCreationFailedException(UserManagementException):
    """Exception raised when user creation fails."""
    def __init__(self, message: str = "User creation failed", error_code: str = "USER_CREATION_FAILED"):
        super().__init__(message, error_code)
class UserUpdateFailedException(UserManagementException):
    """Exception raised when user update fails."""
    def __init__(self, message: str = "User update failed", error_code: str = "USER_UPDATE_FAILED"):
        super().__init__(message, error_code)
class UserDeletionFailedException(UserManagementException):
    """Exception raised when user deletion fails."""
    def __init__(self, message: str = "User deletion failed", error_code: str = "USER_DELETION_FAILED"):
        super().__init__(message, error_code)
class InvalidCredentialsException(UserManagementException):
    """Exception raised when user credentials are invalid."""
    def __init__(self, message: str = "Invalid credentials", error_code: str = "INVALID_CREDENTIALS"):
        super().__init__(message, error_code)
class OCRScanFailedException(UserManagementException):
    """Exception raised when OCR scanning fails."""
    def __init__(self, message: str = "OCR scan failed", error_code: str = "OCR_SCAN_FAILED"):
        super().__init__(message, error_code)
class DataFetchFailedException(UserManagementException):
    """Exception raised when data fetching fails."""
    def __init__(self, message: str = "Data fetch failed", error_code: str = "DATA_FETCH_FAILED"):
        super().__init__(message, error_code)
class BanStudentFailedException(UserManagementException):
    """Exception raised when banning a student fails."""
    def __init__(self, message: str = "Ban student failed", error_code: str = "BAN_STUDENT_FAILED"):
        super().__init__(message, error_code)
class EditStudentStatusFailedException(UserManagementException):
    """Exception raised when editing a student's status fails."""
    def __init__(self, message: str = "Edit student status failed", error_code: str = "EDIT_STUDENT_STATUS_FAILED"):
        super().__init__(message, error_code)
class InvalidTokenException(UserManagementException):
    """Exception raised when a token is invalid."""
    def __init__(self, message: str = "Invalid token", error_code: str = "INVALID_TOKEN"):
        super().__init__(message, error_code)
class InvalidVerificationTokenException(UserManagementException):
    """Exception raised when a verification token is invalid."""
    def __init__(self, message: str = "Invalid verification token", error_code: str = "INVALID_VERIFICATION_TOKEN"):
        super().__init__(message, error_code)
class  InvalidImageError(UserManagementException):
    """Exception raised when an image is invalid."""
    def __init__(self, message: str = "Invalid image", error_code: str = "INVALID_IMAGE"):
        super().__init__(message, error_code)