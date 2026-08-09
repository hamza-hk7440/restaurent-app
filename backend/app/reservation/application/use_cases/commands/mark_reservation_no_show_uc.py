from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from reservation.domain.entities.reservation_entity import Reservation
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.domain.exceptions.domain_exceptions import (
    ReservationNotFoundException,
    InvalidReservationStateException,
)
from reservation.application.dtos.reservation_request_dtos import MarkReservationNoShowCommand
from reservation.application.dtos.reservation_response_dtos import ReservationResponseDTO

class MarkReservationNoShowUseCase:
    ALLOWED_INITIAL_STATUSES = {
        ReservationStatus.CONFIRMED.value,
        ReservationStatus.PENDING.value,
    }

    def __init__(self, reservation_repository: IReservationRepository):
        self._reservation_repo = reservation_repository

    async def execute(self, command: MarkReservationNoShowCommand) -> ReservationResponseDTO:
        reservation = await self._get_reservation_or_raise(command.reservation_id)

        self._verify_restaurant_if_provided(reservation, command.restaurant_id)
        self._verify_can_be_marked_no_show(reservation)

        updated_reservation = await self._apply_no_show(reservation)

        return self._map_to_response_dto(updated_reservation)

    async def _get_reservation_or_raise(self, reservation_id: UUID) -> Reservation:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(
                f"Reservation with ID '{reservation_id}' not found."
            )
        return reservation

    @staticmethod
    def _verify_restaurant_if_provided(
        reservation: Reservation, restaurant_id: Optional[UUID]
    ) -> None:
        if restaurant_id and str(reservation.restaurant_id) != str(restaurant_id):
            raise InvalidReservationStateException(
                f"Reservation '{reservation.id}' does not belong to restaurant '{restaurant_id}'."
            )

    @classmethod
    def _verify_can_be_marked_no_show(cls, reservation: Reservation) -> None:
        status_val = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )

        no_show_target = getattr(ReservationStatus, "NO_SHOW", ReservationStatus.EXPIRED)
        no_show_val = (
            no_show_target.value if hasattr(no_show_target, "value") else str(no_show_target)
        )

        if status_val == no_show_val:
            raise InvalidReservationStateException(
                f"Reservation '{reservation.id}' is already marked as no-show."
            )

        if status_val not in cls.ALLOWED_INITIAL_STATUSES:
            raise InvalidReservationStateException(
                f"Cannot mark reservation as no-show from '{status_val}' status."
            )

    async def _apply_no_show(self, reservation: Reservation) -> Reservation:
        target_status = getattr(ReservationStatus, "NO_SHOW", ReservationStatus.EXPIRED)
        reservation.status = target_status
        reservation.updated_at = datetime.now(timezone.utc)
        await self._reservation_repo.update_status(reservation.id, target_status)
        return reservation

    @staticmethod
    def _map_to_response_dto(reservation: Reservation) -> ReservationResponseDTO:
        status_val = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )

        return ReservationResponseDTO(
            id=UUID(str(reservation.id)),
            student_id=UUID(str(reservation.student_id)),
            restaurant_id=UUID(str(reservation.restaurant_id)),
            status=status_val,
            updated_at=reservation.updated_at or datetime.now(timezone.utc),
        )