from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, ConfigDict,model_validator
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime,time
from reservation.domain.value_objects.meal_category import MealCategory
from reservation.domain.value_objects.meal_availability import MealAvailability
from reservation.domain.value_objects.restaurent_status import RestaurentStatus
class RestaurentResponseDTO(BaseModel):
    id: UUID
    establishment_id: UUID
    name: Annotated[str, Field(description="The name of the restaurant.")]
    adress: Annotated[str, Field(description="The address of the restaurant.")]
    phone: Annotated[str, Field(description="The phone number of the restaurant.")]
    opening_time: Annotated[time, Field(description="The opening time of the restaurant.")]
    closing_time: Annotated[time, Field(description="The closing time of the restaurant.")]
    capacity: Annotated[int, Field(description="The capacity of the restaurant.")]
    status: Annotated[RestaurentStatus, Field(description="The status of the restaurant.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "establishment_id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "The Great Restaurant",
                "adress": "123 Main Street",
                "phone": "555-1234",
                "opening_time": "09:00:00",
                "closing_time": "22:00:00",
                "capacity": 100,
                "status": "open"
            }
        }
    )
    @classmethod
    def from_entity(cls, restaurant) -> 'RestaurentResponseDTO':
        return cls(
            id=restaurant.id,
            establishment_id=restaurant.establishment_id,
            name=restaurant.name,
            adress=restaurant.adress,
            phone=restaurant.phone,
            opening_time=restaurant.opening_time,
            closing_time=restaurant.closing_time,
            capacity=restaurant.capacity,
            status=restaurant.status
        )
class MealResponseDTO(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: Annotated[str, Field(description="The name of the meal.")]
    description: Annotated[str, Field(description="The description of the meal.")]
    price: Annotated[float, Field(description="The price of the meal.")]
    category: Annotated[MealCategory, Field(description="The category of the meal.")]
    availability_status: Annotated[MealAvailability, Field(description="The availability of the meal.")]
    meal_code: Annotated[str, Field(description="The unique code of the meal.")]
    photo_url: Annotated[str, Field(description="The URL of the meal's photo.")]
    rating: Annotated[float, Field(description="The rating of the meal.")]
    popularity_score: Annotated[float, Field(description="The popularity score of the meal.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Delicious Pizza",
                "description": "A delicious pizza with a variety of toppings.",
                "price": 12.99,
                "category": "main_course",
                "availability_status": "available",
                "meal_code": "PIZZA001",
                "photo_url": "https://example.com/pizza.jpg",
                "rating": 4.5,
                "popularity_score": 8.2
            }
        }
    )
    @classmethod
    def from_entity(cls, meal) -> 'MealResponseDTO':
        return cls(
            id=meal.id,
            restaurant_id=meal.restaurant_id,
            name=meal.name,
            description=meal.description,
            price=meal.price,
            category=meal.category,
            availability_status=meal.availability_status,
            meal_code=meal.meal_code,
            photo_url=meal.photo_url,
            rating=meal.rating,
            popularity_score=meal.popularity_score
        )
class DailyMenuResponseDTO(BaseModel):
    id: UUID
    restaurant_id: UUID
    date: Annotated[datetime, Field(description="The date of the daily menu.")]
    is_available: Annotated[bool, Field(description="Indicates if the daily menu is available.")]
    meals: Annotated[list[MealResponseDTO], Field(description="The list of meals in the daily menu.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                "date": "2023-10-01T00:00:00",
                "is_available": True,
                "meals": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Delicious Pizza",
                        "description": "A delicious pizza with a variety of toppings.",
                        "price": 12.99,
                        "category": "main_course",
                        "availability_status": "available",
                        "meal_code": "PIZZA001",
                        "photo_url": "https://example.com/pizza.jpg",
                        "rating": 4.5,
                        "popularity_score": 8.2
                    }
                ]
            }
        }
    )
    @classmethod
    def from_entity(cls, daily_menu) -> 'DailyMenuResponseDTO':
        meals_dto = [MealResponseDTO.from_entity(meal) for meal in daily_menu.meals]
        return cls(
            id=daily_menu.id,
            restaurant_id=daily_menu.restaurant_id,
            date=daily_menu.date,
            is_available=daily_menu.is_available,
            meals=meals_dto
        )
@dataclass(frozen=True)
class GetRestaurentsQuery:
    establishment_id: UUID
    status: RestaurentStatus | None = None
@dataclass(frozen=True)
class GetRestaurentDetailsQuery:
    restaurent_id: UUID
@dataclass(frozen=True)
class GetDailyMenuQuery:
    restaurent_id: UUID
    date: datetime
    category: MealCategory | None = None
    search_query: str | None = None


class CreateRestaurantCommand(BaseModel):
    establishment_id: UUID = Field(description="UUID of the establishment that owns the restaurant.")
    name: str = Field(min_length=2, max_length=255)
    address: str = Field(min_length=2, max_length=500)
    phone: str = Field(min_length=3, max_length=50)
    opening_time: datetime
    closing_time: datetime
    capacity: int = Field(ge=0)
    status: RestaurentStatus = Field(default=RestaurentStatus.OPEN)

    model_config = ConfigDict(extra="forbid")


class CreateMealCommand(BaseModel):
    restaurant_id: UUID
    name: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=1)
    price: float = Field(ge=0)
    category: MealCategory
    availability_status: MealAvailability = Field(default=MealAvailability.AVAILABLE)
    meal_code: str = Field(min_length=1, max_length=50)
    photo_url: str = Field(default="", max_length=500)
    rating: float = Field(default=0, ge=0)
    popularity_score: float = Field(default=0, ge=0)

    model_config = ConfigDict(extra="forbid")


class CreateTimeSlotCommand(BaseModel):
    restaurant_id: UUID
    start_time: time
    end_time: time
    capacity: int = Field(gt=0, description="Capacity must be strictly greater than 0.")

    @model_validator(mode="after")
    def validate_model(self) -> "CreateTimeSlotCommand":
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time.")
        return self

class MenuItemInputDTO(BaseModel):
    name: str = Field(min_length=2, max_length=100, description="Name of the food item.")
    category: str = Field(description="Category (e.g., MAIN_COURSE, STARTER, DESSERT, BEVERAGE).")
    description: Optional[str] = Field(default=None, max_length=255)
    calories: Optional[int] = Field(default=None, ge=0)
    allergens: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")
class ManageDailyMenuCommand(BaseModel):
    restaurant_id: UUID = Field(description="UUID of the campus restaurant.")
    target_date: datetime = Field(description="Date for which the menu applies.")
    is_available: bool = Field(description="Indicates if the menu is available for the specified date.")
    notes: Optional[str] = Field(default=None, description="Optional notes for the daily menu.")
    created_by: Optional[UUID] = Field(default=None, description="UUID of the user creating or updating the menu.")
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_date": "2023-10-01T00:00:00",
                "is_available": True,
                "notes": "Special menu for the day.",
                "created_by": "123e4567-e89b-12d3-a456-426614174001"
                
            }
        },
    )


class MenuItemResponseDTO(BaseModel):
    id: UUID
    name: str
    category: str
    description: Optional[str]
    calories: Optional[int]
    allergens: List[str]

    model_config = ConfigDict(extra="forbid")
class RestockMealCommand(BaseModel):
    menu_id: UUID = Field(description="UUID of the daily menu to restock.")
    restaurant_id: Optional[UUID] = Field(
        default=None, 
        description="Optional restaurant UUID to enforce authorization and ownership."
    )
    quantity_to_add: int = Field(
        gt=0, 
        description="Number of available meals to add to the menu's capacity."
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "menu_id": "123e4567-e89b-12d3-a456-426614174010",
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174001",
                "quantity_to_add": 50,
            }
        },
    )


class UpsertDailyMenuMealCommand(BaseModel):
    daily_menu_id: UUID = Field(description="UUID of the daily menu.")
    meal_id: UUID = Field(description="UUID of the meal to add or update on the daily menu.")
    quantity_available: int = Field(
        ge=0,
        description="Total quantity available for this meal on the selected daily menu.",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "daily_menu_id": "123e4567-e89b-12d3-a456-426614174010",
                "meal_id": "123e4567-e89b-12d3-a456-426614174002",
                "quantity_available": 25,
            }
        },
    )


class UpsertDailyMenuMealResponseDTO(BaseModel):
    daily_menu_id: UUID
    meal_id: UUID
    quantity_available: int
    quantity_reserved: int
    remaining_quantity: int
    is_sold_out: bool

    model_config = ConfigDict(extra="forbid")


class RestockMealResponseDTO(BaseModel):
    menu_id: UUID
    restaurant_id: UUID
    previous_quantity: int
    new_quantity: int
    updated_at: datetime

    model_config = ConfigDict(extra="forbid")

class UpdateRestaurantStatusRequest(BaseModel):
    restaurant_id: UUID = Field(description="UUID of the restaurant to update.")
    new_status: RestaurentStatus = Field(description="New status to set for the restaurant.")   
    reason: Optional[str] = Field(default=None, description="Optional reason for the status change.")
class UpdateRestaurantStatusResponseDTO(BaseModel):
    restaurant_id: UUID
    previous_status: RestaurentStatus
    new_status: RestaurentStatus
    message: str
    success: bool
