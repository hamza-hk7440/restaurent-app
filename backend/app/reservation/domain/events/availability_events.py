from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod
from reservation.domain.events.base import DomainEvent

@dataclass
class MealSoldOutEvent(DomainEvent):
    """
    Event: Meal Sold Out
    
    Triggered when: All available quantities of a meal are reserved
    
    Subscribers should:
    - Update meal availability status to SOLD_OUT
    - Notify admin
    - Update menu UI to show sold out
    """
    
    event_type: str = "availability.meal_sold_out"
    meal_id: UUID = None
    restaurant_id: UUID = None
    meal_name: str = None
    sold_out_date: str = None
    
    def get_event_name(self) -> str:
        return "Meal Sold Out"
 
 
@dataclass
class TimeSlotFullEvent(DomainEvent):
    """
    Event: Time Slot Full
    
    Triggered when: All seats in a time slot are reserved
    
    Subscribers should:
    - Update slot availability to show no seats
    - Notify admin
    - Update reservation UI to show slot unavailable
    """
    
    event_type: str = "availability.time_slot_full"
    time_slot_id: UUID = None
    restaurant_id: UUID = None
    slot_time: str = None  # "12:00 - 12:30"
    full_date: str = None
    
    def get_event_name(self) -> str:
        return "Time Slot Full"
 
 
@dataclass
class MealRestockedEvent(DomainEvent):
    """
    Event: Meal Restocked
    
    Triggered when: Admin increases available quantity for a meal
    
    Subscribers should:
    - Update meal availability status back to AVAILABLE
    - Notify waiting students
    - Update UI
    """
    
    event_type: str = "availability.meal_restocked"
    meal_id: UUID = None
    restaurant_id: UUID = None
    meal_name: str = None
    quantity_added: int = 0
    new_total: int = 0
    
    def get_event_name(self) -> str:
        return "Meal Restocked"