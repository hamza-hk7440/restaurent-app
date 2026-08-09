from enum import Enum

class NotificationType(Enum):
    REMINDER_24H = "reminder_24h"
    REMINDER_1H = "reminder_1h"
    CONFIRMATION = "confirmation"
    CANCELLATION = "cancellation"