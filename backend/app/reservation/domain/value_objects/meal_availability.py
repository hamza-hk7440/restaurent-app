from enum import Enum

class MealAvailability(Enum):
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    UNAVAILABLE = "unavailable"