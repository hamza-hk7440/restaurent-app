class DomainException(Exception):

    def __init__(self, message: str,error_code:str="DOMAIN_EXCEPTION"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
class InvalidEntityException(DomainException):
    def __init__(self, message: str,error_code:str="INVALID_ENTITY"):
        super().__init__(message,error_code)
class EntityNotFoundException(DomainException):
    def __init__(self, message: str,error_code:str="ENTITY_NOT_FOUND"):
        super().__init__(message,error_code)
class UnauthorizedAccessException(DomainException):
    def __init__(self, message: str,error_code:str="UNAUTHORIZED_ACCESS"):
        super().__init__(message,error_code)
class BusinessRuleViolationException(DomainException):
    def __init__(self, message: str,error_code:str="BUSINESS_RULE_VIOLATION"):
        super().__init__(message,error_code)
