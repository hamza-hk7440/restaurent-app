class DomainException(Exception):
    def __init__(self, message: str,error_code:str="DOMAIN_EXCEPTION"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
class InvalidEntityException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_ENTITY"):
            super().__init__(message,error_code)
class RestaurantNotFoundException(DomainException):
        def __init__(self, message: str,error_code:str="RESTAURANT_NOT_FOUND"):
            super().__init__(message,error_code)
class MenuNotFoundException(DomainException):
        def __init__(self, message: str,error_code:str="MENU_NOT_FOUND"):
            super().__init__(message,error_code)