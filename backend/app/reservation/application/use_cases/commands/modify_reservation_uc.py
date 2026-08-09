from datetime import datetime, timezone
from typing import List, Tuple, Optional
from uuid import uuid4

from reservation.domain.entities.reservation_entity import Reservation
from reservation.domain.entities.reservation_item_entity import ReservationItemEntity
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.interfaces.restaurent_repo import IRestaurentRepository
from reservation.domain.interfaces.daily_menu_repo import IDailyMenuRepository
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.domain.interfaces.reservation_item_repo import IReservationItemRepository
from reservation.domain.interfaces.time_slot_availability_repo import ITimeSlotAvailabilityRepository
from reservation.domain.exceptions.domain_exceptions import (
    ReservationNotFoundException,
    ReservationModificationNotAllowedException,
    UnauthorizedAccessException,
    DoubleBookingException,
    TimeSlotFullException,
    MenuNotFoundException,
    InsufficientMealStockException,
)
from reservation.application.dtos.reservation_request_dtos import (
    ModifyReservationRequestDTO,
)
from reservation.application.dtos.reservation_response_dtos import (
    ReservationItemResponseDTO,
    ReservationResponseDTO,
)
class ModifyReservationUseCase:
    def __init__(
        self,
        restaurant_repository: IRestaurentRepository,
        time_slot_availability_repository: ITimeSlotAvailabilityRepository,
        daily_menu_repository: IDailyMenuRepository,
        reservation_repository: IReservationRepository,
        reservation_item_repository: IReservationItemRepository,
    ):
        self._restaurant_repo = restaurant_repository
        self._time_slot_availability_repo = time_slot_availability_repository
        self._daily_menu_repo = daily_menu_repository
        self._reservation_repo = reservation_repository
        self._reservation_item_repo = reservation_item_repository

    async def execute(
        self, reservation_id: str, student_id: str, request: ModifyReservationRequestDTO
    ) -> ReservationResponseDTO:
        reservation = await self._get_and_validate_reservation(reservation_id, student_id)

        await self._handle_schedule_change_if_needed(reservation, request)

        total_price, item_entities = await self._process_items_update_if_provided(
            reservation, request
        )

        self._update_reservation_fields(reservation, request, total_price)
        await self._reservation_repo.update(reservation)

        if item_entities is not None:
            await self._sync_reservation_items(reservation.id, item_entities)

        current_items = (
            item_entities
            if item_entities is not None
            else await self._reservation_item_repo.get_by_reservation(reservation_id)
        )

        return self._map_to_response_dto(reservation, current_items)

    async def _get_and_validate_reservation(self, reservation_id: str, student_id: str) -> Reservation:
        reservation = await self._reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")

        if str(reservation.student_id) != str(student_id):
            raise UnauthorizedAccessException("You are not authorized to modify this reservation.")

        status_val = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )
        if status_val in [ReservationStatus.CANCELLED.value, ReservationStatus.COMPLETED.value]:
            raise ReservationModificationNotAllowedException(f"Cannot modify reservation in {status_val} status.")

        return reservation

    async def _handle_schedule_change_if_needed(
        self, reservation: Reservation, request: ModifyReservationRequestDTO
    ) -> None:
        new_date = request.date or reservation.date
        new_slot_id = str(request.time_slot_id) if request.time_slot_id else str(reservation.time_slot_id)

        is_schedule_changed = (new_date != reservation.date) or (new_slot_id != str(reservation.time_slot_id))
        if not is_schedule_changed:
            return

        has_double = await self._reservation_repo.check_double_booking(
            student_id=str(reservation.student_id), date=new_date, time_slot=new_slot_id
        )
        if has_double:
            raise DoubleBookingException("Student already has an active reservation for the target time slot.")

        has_capacity = await self._time_slot_availability_repo.has_capacity(
            restaurant_id=str(reservation.restaurant_id), time_slot_id=new_slot_id, date=new_date
        )
        if not has_capacity:
            raise TimeSlotFullException("Target time slot is fully booked.")

    async def _process_items_update_if_provided(
        self, reservation: Reservation, request: ModifyReservationRequestDTO
    ) -> Tuple[Optional[float], Optional[List[ReservationItemEntity]]]:
        if request.items is None:
            return None, None

        target_date = request.date or reservation.date
        menu = await self._daily_menu_repo.get_by_restaurant_and_date(
            str(reservation.restaurant_id), target_date
        )
        if not menu:
            raise MenuNotFoundException(f"No active menu found for date {target_date}.")

        total_price = 0.0
        item_entities: List[ReservationItemEntity] = []

        for item in request.items:
            subtotal, entity = self._verify_and_create_item_entity(menu, item)
            total_price += subtotal
            item_entities.append(entity)

        return total_price, item_entities

    @staticmethod
    def _verify_and_create_item_entity(menu, item) -> Tuple[float, ReservationItemEntity]:
        meal_id_str = str(item.meal_id)
        meal = next((m for m in menu.meals if str(m.id) == meal_id_str), None)
        if not meal:
            raise InsufficientMealStockException(f"Meal ID {meal_id_str} is not on the daily menu.")

        available_qty = getattr(meal, "quantity_available", 0)
        if available_qty < item.quantity:
            raise InsufficientMealStockException(f"Insufficient stock for meal: {getattr(meal, 'name', meal_id_str)}.")

        unit_price = float(getattr(meal, "price", 0.0))
        subtotal = unit_price * item.quantity

        item_entity = ReservationItemEntity(
            id=str(uuid4()),
            reservation_id="",
            meal_id=meal_id_str,
            quantity=item.quantity,
        )
        return subtotal, item_entity

    @staticmethod
    def _update_reservation_fields(
        reservation: Reservation, request: ModifyReservationRequestDTO, new_price: Optional[float]
    ) -> None:
        if request.date is not None:
            reservation.date = request.date
        if request.time_slot_id is not None:
            reservation.time_slot_id = str(request.time_slot_id)
        if new_price is not None:
            reservation.total_price = new_price
        reservation.updated_at = datetime.now(timezone.utc)

    async def _sync_reservation_items(
        self, reservation_id: str, new_items: List[ReservationItemEntity]
    ) -> None:
        existing_items = await self._reservation_item_repo.get_by_reservation(reservation_id)
        for old_item in existing_items:
            await self._reservation_item_repo.delete(old_item.id)

        for item in new_items:
            item.reservation_id = reservation_id
            await self._reservation_item_repo.create(item)

    @classmethod
    def _map_to_response_dto(
        cls, reservation: Reservation, items: List[ReservationItemEntity]
    ) -> ReservationResponseDTO:
        item_dtos = [cls._map_item_to_dto(item) for item in items]
        status_val = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )

        return ReservationResponseDTO(
            id=reservation.id,
            student_id=reservation.student_id,
            restaurant_id=reservation.restaurant_id,
            restaurant_name=getattr(reservation, "restaurant_name", ""),
            date=reservation.date,
            time_slot_id=reservation.time_slot_id,
            time_slot_label=getattr(reservation, "time_slot_label", ""),
            status=status_val,
            total_price=float(reservation.total_price),
            confirmation_number=getattr(reservation, "confirmation_number", ""),
            qr_code_path=getattr(reservation, "qr_code_path", None),
            items=item_dtos,
            created_at=reservation.created_at,
        )

    @staticmethod
    def _map_item_to_dto(item: ReservationItemEntity) -> ReservationItemResponseDTO:
        return ReservationItemResponseDTO(
            id=item.id,
            meal_id=item.meal_id,
            meal_name=getattr(item, "meal_name", ""),
            quantity=item.quantity,
            unit_price=float(getattr(item, "unit_price", 0.0)),
            subtotal=float(getattr(item, "subtotal", 0.0)),
            notes=getattr(item, "notes", None),
        )