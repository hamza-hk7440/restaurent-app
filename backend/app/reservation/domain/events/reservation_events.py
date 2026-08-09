from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod
from reservation.domain.events.base import DomainEvent
@dataclass
class ReservationCreatedEvent(DomainEvent):
    """
    Event: Reservation Created
    
    Triggered when: Student creates a new reservation
    
    Subscribers should:
    - Deduct balance from student account
    - Reserve meal quantities
    - Reserve time slot seat
    - Create notification
    - Send confirmation email
    """
    
    event_type: str = "reservation.created"
    student_id: UUID = None
    restaurant_id: UUID = None
    reservation_date: str = None  # ISO format date
    time_slot_id: UUID = None
    confirmation_number: str = None
    total_price: float = 0.0
    meals: List[dict] = None  # [{meal_id, quantity, price}, ...]
    
    def get_event_name(self) -> str:
        return "Reservation Created"
 
 
@dataclass
class ReservationConfirmedEvent(DomainEvent):
    """
    Event: Reservation Confirmed
    
    Triggered when: Reservation is confirmed after payment
    
    Subscribers should:
    - Generate QR code
    - Send confirmation email with QR code
    - Send push notification
    - Update reservation status to CONFIRMED
    """
    
    event_type: str = "reservation.confirmed"
    student_id: UUID = None
    confirmation_number: str = None
    restaurant_name: str = None
    reservation_date: str = None
    time_slot: str = None  # "12:00 - 12:30"
    
    def get_event_name(self) -> str:
        return "Reservation Confirmed"
 
 
@dataclass
class ReservationModifiedEvent(DomainEvent):
    """
    Event: Reservation Modified
    
    Triggered when: Student modifies time slot or meals
    
    Subscribers should:
    - Handle price adjustments (top-up or refund)
    - Update reservation items
    - Send modification email
    - Send notification
    """
    event_type: str = "reservation.modified"
    student_id: UUID = None
    modification_type: str = None  # "MEAL" or "TIME_SLOT"
    old_value: str = None
    new_value: str = None
    price_adjustment: float = 0.0  # Positive = top-up, Negative = refund
    requires_top_up: bool = False
    requires_refund: bool = False
    
    def get_event_name(self) -> str:
        return "Reservation Modified"
 
 
@dataclass
class ReservationCancelledEvent(DomainEvent):
    """
    Event: Reservation Cancelled
    
    Triggered when: Student cancels reservation (>= 2 hours before)
    
    Subscribers should:
    - Refund full amount to student balance
    - Release meal quantities
    - Release time slot seat
    - Send cancellation email
    - Send notification
    - Update reservation status to CANCELED
    """
    
    event_type: str = "reservation.cancelled"
    student_id: UUID = None
    confirmation_number: str = None
    refund_amount: float = 0.0
    cancellation_reason: Optional[str] = None
    
    def get_event_name(self) -> str:
        return "Reservation Cancelled"
 
 
@dataclass
class ReservationCompletedEvent(DomainEvent):
    """
    Event: Reservation Completed
    
    Triggered when: Reservation date has passed / student attended
    
    Subscribers should:
    - Update reservation status to COMPLETED
    - Request review/rating
    - Send thank you email
    - Send notification
    """
    
    event_type: str = "reservation.completed"
    student_id: UUID = None
    restaurant_id: UUID = None
    reservation_date: str = None
    
    def get_event_name(self) -> str:
        return "Reservation Completed"
 
 
@dataclass
class ReservationNoShowEvent(DomainEvent):
    """
    Event: Reservation No-Show
    
    Triggered when: Student didn't show up for reservation
    
    Subscribers should:
    - Update reservation status to NO_SHOW
    - Track no-show for future policies
    - Send notification
    """
    
    event_type: str = "reservation.no_show"
    student_id: UUID = None
    restaurant_id: UUID = None
    reservation_date: str = None
    
    def get_event_name(self) -> str:
        return "Reservation No-Show"