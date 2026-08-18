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
class ReservationNotFoundException(DomainException):
        def __init__(self, message: str,error_code:str="RESERVATION_NOT_FOUND"):
            super().__init__(message,error_code)
class UnauthorizedAccessException(DomainException):
        def __init__(self, message: str,error_code:str="UNAUTHORIZED_ACCESS"):
            super().__init__(message,error_code)
class DoubleBookingException(DomainException):
      def __init__(self, message: str,error_code:str="DOUBLE_BOOKING"):
            super().__init__(message,error_code)
class InsufficientMealStockException(DomainException):
      def __init__(self, message: str,error_code:str="INSUFFICIENT_MEAL_STOCK"):
            super().__init__(message,error_code)
class TimeSlotFullException(DomainException):
      def __init__(self, message: str,error_code:str="TIME_SLOT_FULL"):
            super().__init__(message,error_code)
class ReservationModificationNotAllowedException(DomainException):
        def __init__(self, message: str,error_code:str="RESERVATION_MODIFICATION_NOT_ALLOWED"):
                super().__init__(message,error_code)
class ReservationCancellationNotAllowedException(DomainException):
        def __init__(self, message: str,error_code:str="RESERVATION_CANCELLATION_NOT_ALLOWED"):
                super().__init__(message,error_code)
class InvalidPaymentWebhookException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_PAYMENT_WEBHOOK"):
                super().__init__(message,error_code)
class ReservationExpiredException(DomainException):
        def __init__(self, message: str,error_code:str="RESERVATION_EXPIRED"):
                super().__init__(message,error_code)
class ReservationAlreadyUsedException(DomainException):
        def __init__(self, message: str,error_code:str="RESERVATION_ALREADY_USED"):
                super().__init__(message,error_code)
class InvalidQRCodeException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_QR_CODE"):
                super().__init__(message,error_code)
class InvalidReservationStateException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_RESERVATION_STATE"):
                super().__init__(message,error_code)
class NotificationNotFoundException(DomainException):
        def __init__(self, message: str,error_code:str="NOTIFICATION_NOT_FOUND"):
                super().__init__(message,error_code)
class InvalidNotificationStateException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_NOTIFICATION_STATE"):
                super().__init__(message,error_code)
class InvalidMenuDataException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_MENU_DATA"):
                super().__init__(message,error_code)
class InvalidMenuStateException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_MENU_STATE"):
                super().__init__(message,error_code)
class InvalidPaymentWebhookException(DomainException):
        def __init__(self, message: str,error_code:str="INVALID_PAYMENT_WEBHOOK"):
                super().__init__(message,error_code)