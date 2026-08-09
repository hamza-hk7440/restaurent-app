from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod
from reservation.domain.events.base import DomainEvent

@dataclass
class PaymentProcessedEvent(DomainEvent):
    """
    Event: Payment Processed
    
    Triggered when: Payment is successfully processed via Paymee
    
    Subscribers should:
    - Create payment transaction record
    - Deduct amount from student balance
    - Update reservation to CONFIRMED
    """
    
    event_type: str = "payment.processed"
    student_id: UUID = None
    reservation_id: UUID = None
    amount: float = 0.0
    transaction_type: str = None  # "CHARGE", "REFUND", "TOP_UP"
    reference_id: str = None  # External payment provider ID
    payment_method: str = None  # "PAYMEE", "CARD", etc.
    
    def get_event_name(self) -> str:
        return "Payment Processed"
 
 
@dataclass
class PaymentFailedEvent(DomainEvent):
    """
    Event: Payment Failed
    
    Triggered when: Payment processing fails
    
    Subscribers should:
    - Create failed payment transaction record
    - Send error notification to student
    - Send email with retry instructions
    - Release any locked resources
    """
    
    event_type: str = "payment.failed"
    student_id: UUID = None
    reservation_id: Optional[UUID] = None
    amount: float = 0.0
    reference_id: Optional[str] = None
    error_reason: str = None
    
    def get_event_name(self) -> str:
        return "Payment Failed"
 
 
@dataclass
class PaymentRefundedEvent(DomainEvent):
    """
    Event: Payment Refunded
    
    Triggered when: Student's balance is refunded (cancellation or adjustment)
    
    Subscribers should:
    - Create refund transaction record
    - Add amount back to student balance
    - Send refund confirmation email
    - Send notification
    """
    
    event_type: str = "payment.refunded"
    student_id: UUID = None
    reservation_id: Optional[UUID] = None
    amount: float = 0.0
    refund_reason: str = None
    
    def get_event_name(self) -> str:
        return "Payment Refunded"