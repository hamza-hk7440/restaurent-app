from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from abc import ABC, abstractmethod
from reservation.domain.events.base import DomainEvent

@dataclass
class MealAddedEvent(DomainEvent):
    """
    Event: Meal Added
    
    Triggered when: Admin adds new meal to menu
    
    Subscribers should:
    - Create meal availability records
    - Update restaurant menu
    - Notify students
    """
    
    event_type: str = "meal.added"
    restaurant_id: UUID = None
    meal_id: UUID = None
    meal_name: str = None
    category: str = None
    price: float = 0.0
    
    def get_event_name(self) -> str:
        return "Meal Added"
 
 
@dataclass
class MealRemovedEvent(DomainEvent):
    """
    Event: Meal Removed
    
    Triggered when: Admin removes meal from menu
    
    Subscribers should:
    - Archive meal
    - Remove from daily menu
    - Notify students about unavailability
    """
    
    event_type: str = "meal.removed"
    restaurant_id: UUID = None
    meal_id: UUID = None
    meal_name: str = None
    reason: Optional[str] = None
    
    def get_event_name(self) -> str:
        return "Meal Removed"
 
 
@dataclass
class RestaurantStatusChangedEvent(DomainEvent):
    """
    Event: Restaurant Status Changed
    
    Triggered when: Admin changes restaurant status (OPEN/CLOSED/PAUSED)
    
    Subscribers should:
    - Update restaurant availability
    - Notify students about closure
    - Handle existing reservations if closed
    """
    
    event_type: str = "restaurant.status_changed"
    restaurant_id: UUID = None
    restaurant_name: str = None
    old_status: str = None
    new_status: str = None
    reason: Optional[str] = None
    
    def get_event_name(self) -> str:
        return "Restaurant Status Changed"