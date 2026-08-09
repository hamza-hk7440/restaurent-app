from typing import List, Set
from uuid import UUID

from reservation.domain.exceptions.domain_exceptions import RestaurantNotFoundException
from reservation.domain.interfaces.restaurent_repo import IRestaurentRepository
from reservation.domain.interfaces.time_slot_repo import ITimeSlotRepository
from reservation.domain.interfaces.time_slot_availability_repo import ITimeSlotAvailabilityRepository
from reservation.application.dtos.availability_dtos import GetAvailbleTimeSlotsQuery, TimeSlotResponseDTO


class GetAvailableTimeSlotsUseCase:
    def __init__(
        self,
        restaurant_repository: IRestaurentRepository,
        time_slot_repository: ITimeSlotRepository,
        time_slot_availability_repository: ITimeSlotAvailabilityRepository,
    ):
        self._restaurant_repo = restaurant_repository
        self._time_slot_repo = time_slot_repository
        self._time_slot_availability_repo = time_slot_availability_repository

    async def execute(self, query: GetAvailbleTimeSlotsQuery) -> List[TimeSlotResponseDTO]:
        await self._ensure_restaurant_exists(query.restaurant_id)

        time_slots = await self._time_slot_repo.get_by_restaurent(query.restaurant_id)
        availabilities = await self._time_slot_availability_repo.get_available_slots(
            restaurent_id=query.restaurant_id,
            date=query.date
        )

        available_ids = {slot.id for slot in availabilities}
        return self._filter_and_map_slots(time_slots, available_ids)

    async def _ensure_restaurant_exists(self, restaurant_id: UUID) -> None:
        restaurant = await self._restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurant_id} not found.")

    @staticmethod
    def _filter_and_map_slots(time_slots: list, available_ids: Set[UUID]) -> List[TimeSlotResponseDTO]:
        return [
            TimeSlotResponseDTO.from_entity(slot)
            for slot in time_slots
            if slot.id in available_ids
        ]