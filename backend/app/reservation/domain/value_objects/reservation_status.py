from enum import Enum

class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "CANCELED"
    CANCELLED = CANCELED
    COMPLETED = "completed"
    NO_SHOW = "no_show"
