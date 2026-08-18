from datetime import date
from typing import List
from uuid import UUID
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.application.dtos.reservation_response_dtos import ReservationSummaryDTO,GetStudentReservationsQuery

class GetStudentReservationsUseCase:
    def __init__(self, reservation_repository: IReservationRepository):
        self.reservation_repository = reservation_repository

    async def execute(self, query: GetStudentReservationsQuery) -> List[ReservationSummaryDTO]:
        reservations = await self.reservation_repository.get_by_student_id(query.student_id)
        filtered_reservations = self._filter_reservations(reservations, query.filter_type)
        return [ReservationSummaryDTO.from_entity(reservation) for reservation in filtered_reservations]
    @classmethod
    def _filter_reservations(cls, reservations, filter_type):
        today = date.today()
        is_upcoming = filter_type == "UPCOMING"
        return[
            res for res in reservations if cls._is_matching_filter(res.date, today, is_upcoming)

        ]
    @classmethod
    def _is_matching_filter(res_date:date,today:date,is_upcoming:bool)->bool:
        res_day = res_date.date() if hasattr(res_date, "date") else res_date
        if is_upcoming:
            return res_day >= today
        else:
            return res_day < today
