from typing import Optional
from reservation.domain.entities.reservation_entity import Reservation
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.domain.exceptions.domain_exceptions import (
    ReservationNotFoundException,
    UnauthorizedAccessException,
    ReservationCancellationNotAllowedException,
)
from reservation.application.dtos.reservation_request_dtos import (
    CancelReservationCommand,
    
)
from reservation.application.dtos.reservation_response_dtos import (
    CancelReservationResponseDTO,)
class CancelReservationUseCase:
    def __init__(self, reservation_repository: IReservationRepository):
        self._reservation_repo = reservation_repository
    async def execute(self, command: CancelReservationCommand) -> CancelReservationResponseDTO:
        reservation = await self._get_and_validate_reservation(command.reservation_id, command.student_id)
        await self._reservation_repo.cancel(reservation.id)
        return self._map_to_response_dto(reservation.id)
    async def _get_and_validate_reservation(self, reservation_id: str, student_id: str) -> Reservation:
        reservation = await self._reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        if str(reservation.student_id) != str(student_id):
            raise UnauthorizedAccessException("You are not authorized to cancel this reservation.")
        self._ensure_cancellation_allowed(reservation.status)
        return reservation
    @staticmethod
    def _ensure_cancellation_allowed(status) -> None:
        status_val = status.value if hasattr(status, "value") else str(status)
        if status_val == ReservationStatus.CANCELLED.value:
            raise ReservationCancellationNotAllowedException("Reservation is already cancelled.")
        if status_val == ReservationStatus.COMPLETED.value:
            raise ReservationCancellationNotAllowedException("Cannot cancel a completed reservation.")
    @staticmethod
    def _map_to_response_dto(reservation_id: str) -> CancelReservationResponseDTO:
        return CancelReservationResponseDTO(
            reservation_id=reservation_id,
            status=ReservationStatus.CANCELLED.value,
            message="Reservation cancelled successfully.",
        )