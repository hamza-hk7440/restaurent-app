class DomainException(Exception):
    def __init__(self, message: str,error_code:str="DOMAIN_EXCEPTION"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
class InvalidEntityException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_ENTITY"):
            super().__init__(message,error_code)