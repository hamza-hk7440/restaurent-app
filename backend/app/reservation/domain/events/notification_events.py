from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod
from reservation.domain.events.base import DomainEvent

@dataclass
class NotificationSentEvent(DomainEvent):
    """
    Event: Notification Sent
    
    Triggered when: Push notification successfully sent to student
    
    Subscribers should:
    - Update notification status to SENT
    - Log notification delivery
    """
    
    event_type: str = "notification.sent"
    student_id: UUID = None
    notification_type: str = None  # "REMINDER_24H", "REMINDER_1H", etc.
    message: str = None
    sent_at: datetime = None
    
    def get_event_name(self) -> str:
        return "Notification Sent"
 
 
@dataclass
class NotificationFailedEvent(DomainEvent):
    """
    Event: Notification Failed
    
    Triggered when: Push notification fails to send
    
    Subscribers should:
    - Update notification status to FAILED
    - Retry sending (with backoff)
    - Log failure reason
    """
    
    event_type: str = "notification.failed"
    student_id: UUID = None
    notification_type: str = None
    error_reason: str = None
    retry_count: int = 0
    
    def get_event_name(self) -> str:
        return "Notification Failed"
 
 
@dataclass
class NotificationReadEvent(DomainEvent):
    """
    Event: Notification Read
    
    Triggered when: Student clicks/reads a notification
    
    Subscribers should:
    - Update notification status to CLICKED
    - Track engagement metrics
    """
    
    event_type: str = "notification.read"
    student_id: UUID = None
    notification_type: str = None
    read_at: datetime = None
    
    def get_event_name(self) -> str:
        return "Notification Read"
 
 
@dataclass
class ReminderScheduledEvent(DomainEvent):
    """
    Event: Reminder Scheduled
    
    Triggered when: 24h or 1h reminder is scheduled for a reservation
    
    Subscribers should:
    - Add to scheduler queue
    - Set reminder time
    - Track scheduled reminders
    """
    
    event_type: str = "notification.reminder_scheduled"
    reservation_id: UUID = None
    student_id: UUID = None
    reminder_type: str = None  # "24H" or "1H"
    scheduled_send_time: datetime = None
    
    def get_event_name(self) -> str:
        return "Reminder Scheduled"