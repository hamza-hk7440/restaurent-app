
from fastapi import APIRouter, Depends,Query, HTTPException, status
from sqlalchemy.exc import IntegrityError
from reservation.application.dtos.catalog_and_menu_dtos import CreateMealCommand, CreateRestaurantCommand, CreateTimeSlotCommand, ManageDailyMenuCommand, RestockMealCommand, UpsertDailyMenuMealCommand
from reservation.domain.value_objects.restaurent_status import RestaurentStatus
from reservation.presentation.controllers.reservation_controller import ReservationController
from reservation.presentation.dependencies import get_reservation_controller
from reservation.application.dtos.payment_and_notification_dtos import SendScheduledRemindersCommand

router = APIRouter(prefix="/admin", tags=["reservation-admin"])


@router.post("/restaurants/{restaurant_id}/status")
async def update_restaurant_status(
    restaurant_id: str,
    new_status: RestaurentStatus,
    reason: str | None = None,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.update_restaurant_status(restaurant_id, new_status, reason)


@router.post("/restaurants")
async def create_restaurant(
    command: CreateRestaurantCommand,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.create_restaurant(command)


@router.post("/meals")
async def create_meal(
    command: CreateMealCommand,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.create_meal(command)


@router.post("/time-slots")
async def create_time_slot(command: CreateTimeSlotCommand, controller: ReservationController = Depends(get_reservation_controller)):
    try:
        return await controller.create_time_slot(command)
    except IntegrityError as e:
        if "time_slots_restaurant_id_start_time_end_time_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A time slot with this start and end time already exists for this restaurant.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity constraint violated.",
        )


@router.post("/reservations/{reservation_id}/complete")
async def mark_reservation_completed(
    reservation_id: str,
    student_id: str | None = None,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.mark_reservation_completed(reservation_id, student_id)


@router.get("/reservations/{reservation_id}")
async def get_reservation_details(
    reservation_id: str,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.get_reservation_admin(reservation_id)


@router.delete("/reservations/{reservation_id}")
async def cancel_reservation(
    reservation_id: str,
    reason: str | None = None,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.cancel_reservation_admin(reservation_id, reason)


@router.post("/reservations/{reservation_id}/no-show")
async def mark_reservation_no_show(
    reservation_id: str,
    student_id: str | None = None,
    reason: str | None = None,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.mark_reservation_no_show(reservation_id, student_id, reason)


@router.post("/notifications/reminders")
async def send_scheduled_reminders(
    command: SendScheduledRemindersCommand,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.send_scheduled_reminders(command)


@router.post("/daily-menus")
async def manage_daily_menu(
    command: ManageDailyMenuCommand,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.manage_daily_menu(command)


@router.post("/daily-menus/restock")
async def restock_meal(
    command: RestockMealCommand,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.restock_meal(command)


@router.post("/daily-menus/meals")
async def upsert_daily_menu_meal(
    command: UpsertDailyMenuMealCommand,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.upsert_daily_menu_meal(command)


@router.post("/reservations/{reservation_id}/validate-qr")
async def validate_qr_code(
    reservation_id: str,
    qr_code_data: str,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.validate_qr_code(reservation_id, qr_code_data)
