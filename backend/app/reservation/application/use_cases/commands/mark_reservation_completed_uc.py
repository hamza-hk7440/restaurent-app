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
from reservation.application.dtos.reservation_request_dtos import MarkReservationCompletedCommand
from reservation.application.dtos.reservation_response_dtos import ReservationResponseDTO


class MarkReservationCompletedUseCase:
    ALLOWED_INITIAL_STATUSES = {ReservationStatus.CONFIRMED.value}

    def __init__(self, reservation_repository: IReservationRepository):
        self._reservation_repo = reservation_repository

    async def execute(self, command: MarkReservationCompletedCommand) -> ReservationResponseDTO:
        reservation = await self._get_reservation_or_raise(command.reservation_id)

        self._verify_ownership_if_provided(reservation, command.student_id)
        self._verify_can_be_completed(reservation)

        updated_reservation = await self._apply_completion(reservation)

        return self._map_to_response_dto(updated_reservation)

    async def _get_reservation_or_raise(self, reservation_id: UUID) -> Reservation:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(
                f"Reservation with ID '{reservation_id}' not found."
            )
        return reservation

    @staticmethod
    def _verify_ownership_if_provided(
        reservation: Reservation, student_id: Optional[UUID]
    ) -> None:
        if student_id and str(reservation.student_id) != str(student_id):
            raise InvalidReservationStateException(
                f"Reservation '{reservation.id}' does not belong to student '{student_id}'."
            )

    @classmethod
    def _verify_can_be_completed(cls, reservation: Reservation) -> None:
        status_val = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )

        if status_val == ReservationStatus.COMPLETED.value:
            raise InvalidReservationStateException(
                f"Reservation '{reservation.id}' is already marked as completed."
            )

        if status_val not in cls.ALLOWED_INITIAL_STATUSES:
            raise InvalidReservationStateException(
                f"Cannot complete reservation in '{status_val}' status. Must be in 'CONFIRMED' status."
            )

    async def _apply_completion(self, reservation: Reservation) -> Reservation:
        reservation.status = ReservationStatus.COMPLETED
        reservation.updated_at = datetime.now(timezone.utc)
        await self._reservation_repo.update_status(reservation.id, ReservationStatus.COMPLETED)
        return reservation

    @staticmethod
    def _map_to_response_dto(reservation: Reservation) -> ReservationResponseDTO:
        return ReservationResponseDTO(
            id=UUID(str(reservation.id)),
            student_id=UUID(str(reservation.student_id)),
            restaurant_id=UUID(str(reservation.restaurant_id)),
            status=ReservationStatus.COMPLETED.value,
            updated_at=reservation.updated_at or datetime.now(timezone.utc),
        )