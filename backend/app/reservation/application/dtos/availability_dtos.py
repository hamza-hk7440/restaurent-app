from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime

class TimeSlotResponseDTO(BaseModel):
    id: UUID
    restaurant_id: UUID
    start_time: Annotated[datetime, Field(description="The start time of the time slot.")]
    end_time: Annotated[datetime, Field(description="The end time of the time slot.")]
    capacity: Annotated[int, Field(description="The capacity of the time slot.")]
    available_seats: Annotated[int, Field(description="The number of available seats in the time slot.")]
    is_full: Annotated[bool, Field(description="Indicates whether the time slot is full or not.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                "start_time": "2023-10-01T12:00:00",
                "end_time": "2023-10-01T14:00:00",
                "capacity": 50,
                "available_seats": 25,
                "is_full": False
            }
        }
    )
    @classmethod
    def from_entity(cls, time_slot) -> 'TimeSlotResponseDTO':
        return cls(
            id=time_slot.id,
            restaurant_id=time_slot.restaurant_id,
            start_time=time_slot.start_time,
            end_time=time_slot.end_time,
            capacity=time_slot.capacity,
            available_seats=time_slot.available_seats,
            is_full=time_slot.is_full
        )
class MealAvailabilityResponseDTO(BaseModel):
    meal_id: UUID
    daily_menu_id: UUID
    quantity_available: Annotated[int, Field(description="The quantity of the meal available for the specified daily menu.")]
    quantity_reserved: Annotated[int, Field(description="The quantity of the meal reserved for the specified daily menu.")]
    remaining_quantity: Annotated[int, Field(description="The remaining quantity of the meal available for the specified daily menu.")]
    is_sold_out: Annotated[bool, Field(description="Indicates whether the meal is sold out for the specified daily menu.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "meal_id": "123e4567-e89b-12d3-a456-426614174002",
                "daily_menu_id": "123e4567-e89b-12d3-a456-426614174003",
                "quantity_available": 100,
                "quantity_reserved": 75,
                "remaining_quantity": 25,
                "is_sold_out": False
            }
        }
    )
    @classmethod
    def from_entity(cls, meal_availability) -> 'MealAvailabilityResponseDTO':
        return cls(
            meal_id=meal_availability.meal_id,
            daily_menu_id=meal_availability.daily_menu_id,
            quantity_available=meal_availability.quantity_available,
            quantity_reserved=meal_availability.quantity_reserved,
            remaining_quantity=meal_availability.remaining_quantity,
            is_sold_out=meal_availability.is_sold_out
        )