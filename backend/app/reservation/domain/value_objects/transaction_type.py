from enum import Enum

class TransactionType(Enum):
    CHARGE = "charge"
    REFUND = "refund"
    TOP_UP = "top_up"
    