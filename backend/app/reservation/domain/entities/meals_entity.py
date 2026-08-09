from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from reservation.domain.exceptions.domain_exceptions import InvalidEntityException
from reservation.domain.value_objects.meal_availability import MealAvailability
from reservation.domain.value_objects.meal_category import MealCategory

class Meal:
    id: UUID
    name: str
    description: str
    price: float
    category: MealCategory
    availability_status: MealAvailability
    meal_code: str
    photo_url: str
    rating: float
    popularity_score: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str, description: str, price: float, category: MealCategory, availability_status: MealAvailability, meal_code: str, photo_url: str, rating: float, popularity_score: float) -> 'Meal':
        if not name or not description or price is None or not category or not availability_status or not meal_code or not photo_url or rating is None or popularity_score is None:
            raise InvalidEntityException("All fields are required to create a Meal.")
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            price=price,
            category=category,
            availability_status=availability_status,
            meal_code=meal_code,
            photo_url=photo_url,
            rating=rating,
            popularity_score=popularity_score,
            created_at=now,
            updated_at=now
        )