from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from user_management.infrastructure.config.database import get_db

from reservation.infrastructure.database.repositories import (
    DailyMenuRepository,
    MealAvailabilityRepository,
    MealRepository,
    NotificationRepository,
    PaymentTransactionRepository,
    ReservationItemRepository,
    ReservationModificationRepository,
    ReservationRepository,
    RestaurantRepository,
    TimeSlotAvailabilityRepository,
    TimeSlotRepository,
)


def get_restaurant_repository(session: AsyncSession = Depends(get_db)) -> RestaurantRepository:
    return RestaurantRepository(session)


def get_time_slot_repository(session: AsyncSession = Depends(get_db)) -> TimeSlotRepository:
    return TimeSlotRepository(session)


def get_daily_menu_repository(session: AsyncSession = Depends(get_db)) -> DailyMenuRepository:
    return DailyMenuRepository(session)


def get_meal_repository(session: AsyncSession = Depends(get_db)) -> MealRepository:
    return MealRepository(session)


def get_meal_availability_repository(session: AsyncSession = Depends(get_db)) -> MealAvailabilityRepository:
    return MealAvailabilityRepository(session)


def get_time_slot_availability_repository(session: AsyncSession = Depends(get_db)) -> TimeSlotAvailabilityRepository:
    return TimeSlotAvailabilityRepository(session)


def get_reservation_repository(session: AsyncSession = Depends(get_db)) -> ReservationRepository:
    return ReservationRepository(session)


def get_reservation_item_repository(session: AsyncSession = Depends(get_db)) -> ReservationItemRepository:
    return ReservationItemRepository(session)


def get_reservation_modification_repository(session: AsyncSession = Depends(get_db)) -> ReservationModificationRepository:
    return ReservationModificationRepository(session)


def get_notification_repository(session: AsyncSession = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(session)


def get_payment_transaction_repository(session: AsyncSession = Depends(get_db)) -> PaymentTransactionRepository:
    return PaymentTransactionRepository(session)
