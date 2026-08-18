from fastapi import APIRouter, Depends, Query

from reservation.domain.value_objects.notification_status import NotificationStatus
from reservation.presentation.dependencies import get_reservation_controller
from reservation.presentation.controllers.reservation_controller import ReservationController

router = APIRouter(prefix="/notifications", tags=["reservation-notifications"])


@router.get("")
async def list_notifications(
    student_id: str,
    limit: int = Query(default=50),
    offset: int = Query(default=0),
    status: NotificationStatus | None = Query(default=None),
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.list_notifications(student_id, limit, offset, status)


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    student_id: str | None = Query(default=None),
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.mark_notification_read(notification_id, student_id)
