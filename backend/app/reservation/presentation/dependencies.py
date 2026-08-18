from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from user_management.infrastructure.config.database import get_db

from reservation.infrastructure.config.di import (
    get_daily_menu_repository,
    get_meal_availability_repository,
    get_meal_repository,
    get_notification_repository,
    get_payment_transaction_repository,
    get_reservation_item_repository,
    get_reservation_modification_repository,
    get_reservation_repository,
    get_restaurant_repository,
    get_time_slot_availability_repository,
    get_time_slot_repository,
)
from reservation.presentation.controllers.reservation_controller import ReservationController


def get_reservation_controller(
    db_session: AsyncSession = Depends(get_db),
) -> ReservationController:
    return ReservationController(
        restaurant_repository=get_restaurant_repository(db_session),
        time_slot_repository=get_time_slot_repository(db_session),
        daily_menu_repository=get_daily_menu_repository(db_session),
        meal_repository=get_meal_repository(db_session),
        meal_availability_repository=get_meal_availability_repository(db_session),
        time_slot_availability_repository=get_time_slot_availability_repository(db_session),
        reservation_repository=get_reservation_repository(db_session),
        reservation_item_repository=get_reservation_item_repository(db_session),
        reservation_modification_repository=get_reservation_modification_repository(db_session),
        notification_repository=get_notification_repository(db_session),
        payment_transaction_repository=get_payment_transaction_repository(db_session),
    )
