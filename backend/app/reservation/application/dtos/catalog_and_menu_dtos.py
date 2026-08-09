from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime
from reservation.domain.value_objects.meal_category import MealCategory
from reservation.domain.value_objects.meal_availability import MealAvailability
from reservation.domain.value_objects.restaurent_status import RestaurentStatus
class RestaurentResponseDTO(BaseModel):
    id: UUID
    establishment_id: UUID
    name: Annotated[str, Field(description="The name of the restaurant.")]
    adress: Annotated[str, Field(description="The address of the restaurant.")]
    phone: Annotated[str, Field(description="The phone number of the restaurant.")]
    opening_time: Annotated[datetime, Field(description="The opening time of the restaurant.")]
    closing_time: Annotated[datetime, Field(description="The closing time of the restaurant.")]
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