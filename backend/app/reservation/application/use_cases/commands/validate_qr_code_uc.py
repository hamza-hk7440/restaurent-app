from datetime import datetime, date, timezone
from uuid import UUID

from reservation.domain.entities.reservation_entity import Reservation
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.domain.exceptions.domain_exceptions import (
    ReservationNotFoundException,
    InvalidQRCodeException,
    ReservationAlreadyUsedException,
    ReservationExpiredException,
)
from reservation.application.dtos.reservation_request_dtos import (
    ValidateQrCodeCommand,
    ValidateQrCodeResponseDTO,
)
class ValidateQRCodeUseCase:
    def __init__(self, reservation_repository: IReservationRepository):
        self._reservation_repo = reservation_repository

    async def execute(self, command: ValidateQrCodeCommand) -> ValidateQrCodeResponseDTO:
        reservation = await self._get_reservation_by_qr_or_raise(command.qr_code_data)

        self._verify_restaurant_match(reservation, command.restaurant_id)
        self._verify_reservation_status(reservation)
        self._verify_reservation_date(reservation)

        await self._mark_as_completed(reservation)

        return self._map_to_response_dto(reservation)

    async def _get_reservation_by_qr_or_raise(self, qr_code_data: str) -> Reservation:
        if not qr_code_data or not qr_code_data.strip():
            raise InvalidQRCodeException("Scanned QR code payload cannot be empty.")

        reservation = await self._reservation_repo.get_by_qr_code(qr_code_data.strip())
        if not reservation:
            raise ReservationNotFoundException("No active reservation found for the provided QR code.")
        return reservation

    @staticmethod
    def _verify_restaurant_match(reservation: Reservation, restaurant_id: UUID) -> None:
        if str(reservation.restaurant_id) != str(restaurant_id):
            raise InvalidQRCodeException("This reservation is not valid for this restaurant location.")

    @staticmethod
    def _verify_reservation_status(reservation: Reservation) -> None:
        status_val = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )

        if status_val == ReservationStatus.COMPLETED.value:
            raise ReservationAlreadyUsedException("This QR code has already been scanned and redeemed.")

        if status_val != ReservationStatus.CONFIRMED.value:
            raise InvalidQRCodeException(f"Reservation cannot be validated in '{status_val}' status.")

    @staticmethod
    def _verify_reservation_date(reservation: Reservation) -> None:
        today = date.today()
        res_date = reservation.date if isinstance(reservation.date, date) else date.fromisoformat(str(reservation.date))

        if res_date < today:
            raise ReservationExpiredException("This reservation has expired.")
        if res_date > today:
            raise InvalidQRCodeException("This reservation is scheduled for a future date.")

    async def _mark_as_completed(self, reservation: Reservation) -> None:
        reservation.status = ReservationStatus.COMPLETED
        reservation.updated_at = datetime.now(timezone.utc)
        await self._reservation_repo.update_status(reservation.id, ReservationStatus.COMPLETED)

    @staticmethod
    def _map_to_response_dto(reservation: Reservation) -> ValidateQrCodeResponseDTO:
        return ValidateQrCodeResponseDTO(
            reservation_id=UUID(str(reservation.id)),
            student_id=UUID(str(reservation.student_id)),
            status=ReservationStatus.COMPLETED.value,
            is_valid=True,
            message="QR Code successfully validated. Meal access granted.",
            validated_at=datetime.now(timezone.utc),
        )