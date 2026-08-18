from fastapi import APIRouter, Depends, Query

from reservation.application.dtos.reservation_request_dtos import CancelReservationRequestDTO, CreateReservationLockCommand, CreateReservationRequestDTO, ModifyReservationRequestDTO
from reservation.presentation.dependencies import get_reservation_controller
from reservation.presentation.controllers.reservation_controller import ReservationController

router = APIRouter(prefix="/reservations", tags=["reservation"])


@router.post("/locks")
async def create_reservation_lock(
    command: CreateReservationLockCommand,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.create_reservation_lock(command)


@router.post("")
async def create_reservation(
    request: CreateReservationRequestDTO,
    student_id: str = Query(...),
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.create_reservation(request, student_id)


@router.get("/{reservation_id}")
async def get_reservation_details(
    reservation_id: str,
    student_id: str = Query(...),
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.get_reservation_details(reservation_id, student_id)


@router.get("/students/{student_id}")
async def list_student_reservations(
    student_id: str,
    filter_type: str = Query(default="UPCOMING"),
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.list_student_reservations(student_id, filter_type)


@router.patch("/{reservation_id}")
async def modify_reservation(
    reservation_id: str,
    student_id: str = Query(...),
    request: ModifyReservationRequestDTO = ..., 
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.modify_reservation(reservation_id, student_id, request)


@router.delete("/{reservation_id}")
async def cancel_reservation(
    reservation_id: str,
    student_id: str = Query(...),
    request: CancelReservationRequestDTO | None = None,
    controller: ReservationController = Depends(get_reservation_controller),
):
    return await controller.cancel_reservation(reservation_id, student_id, request)
