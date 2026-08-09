from typing import List, Set
from uuid import UUID
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.application.dtos.reservation_response_dtos import GetReservationDetailsQuery,ReservationResponseDTO,ReservationItemResponseDTO
from reservation.domain.exceptions.domain_exceptions import UnauthorizedAccessException,ReservationNotFoundException
class GetReservationDetailsUseCase:
    def __init__(self, reservation_repository: IReservationRepository):
        self.reservation_repository = reservation_repository

    async def execute(self, query: GetReservationDetailsQuery) -> ReservationResponseDTO:
        reservation = await self._get_reservation_or_raise(query.reservation_id, query.student_id)
        return self._map_to_response_dto(reservation, query.student_id)

    async def _get_reservation_or_raise(self, reservation_id: UUID, student_id: UUID):
        reservation = await self.reservation_repository.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        if reservation.student_id != student_id:
            raise UnauthorizedAccessException(f"Student with ID {student_id} is not authorized to access this reservation.")
        return reservation
    @classmethod
    def _map_to_response_dto(cls, reservation, student_id: UUID) -> ReservationResponseDTO:
        items_dto = [ReservationItemResponseDTO.from_entity(item) for item in reservation.items]
        return ReservationResponseDTO(
            id=reservation.id,
            restaurent_id=reservation.restaurent_id,
            student_id=student_id,
            restaurent_name=reservation.restaurent_name,
            date=reservation.date,
            time_slot_id=reservation.time_slot_id,
            confirmation_code=reservation.confirmation_code,
            qr_code_path=reservation.qr_code_path,
            items=items_dto,
            created_at=reservation.created_at
        )