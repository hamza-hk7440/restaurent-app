from fastapi import APIRouter, Depends, Query

from reservation.domain.value_objects.restaurent_status import RestaurentStatus
from reservation.presentation.dependencies import get_reservation_controller
from reservation.presentation.controllers.reservation_controller import ReservationController

router = APIRouter(prefix="/catalog", tags=["reservation-catalog"])


@router.get("/restaurants")
async def list_restaurants(
    establishment_id: str = Query(...),
    status: RestaurentStatus | None = Query(default=None),
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.list_restaurants(establishment_id, status)


@router.get("/restaurants/{restaurent_id}")
async def get_restaurant(
    restaurent_id: str,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.get_restaurant(restaurent_id)


@router.get("/restaurants/{restaurent_id}/daily-menu")
async def get_daily_menu(
    restaurent_id: str,
    date: str = Query(...),
    category: str | None = Query(default=None),
    search_query: str | None = Query(default=None),
    controller: ReservationController = Depends(get_reservation_controller),
):
    from datetime import datetime

    return await controller.get_daily_menu(restaurent_id, datetime.fromisoformat(date), category, search_query)


@router.get("/restaurants/{restaurent_id}/available-days")
async def get_available_days(
    restaurent_id: str,
    start_date: str | None = Query(default=None),
    days_ahead: int = Query(default=7),
    controller: ReservationController = Depends(get_reservation_controller),
):
    from datetime import datetime

    parsed_start = datetime.fromisoformat(start_date) if start_date else None
    return await controller.get_available_days(restaurent_id, parsed_start, days_ahead)


@router.get("/restaurants/{restaurent_id}/time-slots")
async def get_available_time_slots(
    restaurent_id: str,
    date: str = Query(...),
    controller: ReservationController = Depends(get_reservation_controller),
):
    from datetime import datetime

    return await controller.get_available_time_slots(restaurent_id, datetime.fromisoformat(date))
