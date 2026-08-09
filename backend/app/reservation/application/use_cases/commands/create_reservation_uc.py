from datetime import datetime, timezone
from typing import List, Tuple
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
    RestaurantNotFoundException,
    DoubleBookingException,
    InsufficientMealStockException,
    TimeSlotFullException,
    MenuNotFoundException,
)
from reservation.application.dtos.reservation_request_dtos import (
    CreateReservationRequestDTO
)
from reservation.application.dtos.reservation_response_dtos import (
    ReservationItemResponseDTO,
    ReservationResponseDTO,
)
class CreateReservationUseCase:
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

    async def execute(self, request: CreateReservationRequestDTO, student_id: str) -> ReservationResponseDTO:
        await self._ensure_no_double_booking(student_id, request.date, str(request.time_slot_id))
        await self._ensure_restaurant_exists(str(request.restaurant_id))
        await self._verify_time_slot_capacity(str(request.restaurant_id), str(request.time_slot_id), request.date)

        total_price, item_entities = await self._process_reservation_items(
            str(request.restaurant_id), request.date, request.items
        )

        reservation = self._build_confirmed_reservation(request, student_id, total_price)
        reservation_id = await self._reservation_repo.create(reservation)

        await self._persist_reservation_items(reservation_id, item_entities)

        return self._map_to_response_dto(reservation, reservation_id, item_entities)

    async def _ensure_no_double_booking(self, student_id: str, lock_date: datetime, time_slot: str) -> None:
        has_double = await self._reservation_repo.check_double_booking(student_id, lock_date, time_slot)
        if has_double:
            raise DoubleBookingException("Student already has an active reservation for this time slot.")

    async def _ensure_restaurant_exists(self, restaurant_id: str) -> None:
        restaurant = await self._restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurant_id} not found.")

    async def _verify_time_slot_capacity(self, restaurant_id: str, time_slot_id: str, lock_date) -> None:
        has_capacity = await self._time_slot_availability_repo.has_capacity(
            restaurant_id=restaurant_id, time_slot_id=time_slot_id, date=lock_date
        )
        if not has_capacity:
            raise TimeSlotFullException("Selected time slot is fully booked.")

    async def _process_reservation_items(
        self, restaurant_id: str, date_val, items: list
    ) -> Tuple[float, List[ReservationItemEntity]]:
        menu = await self._daily_menu_repo.get_by_restaurant_and_date(restaurant_id, date_val)
        if not menu:
            raise MenuNotFoundException(f"No active menu found for date {date_val}.")

        total_price = 0.0
        item_entities: List[ReservationItemEntity] = []

        for item in items:
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
            reservation_id="",  # Linked after reservation creation
            meal_id=meal_id_str,
            quantity=item.quantity,
        )
        return subtotal, item_entity

    @classmethod
    def _build_confirmed_reservation(
        cls, request: CreateReservationRequestDTO, student_id: str, total_price: float
    ) -> Reservation:
        res_id = str(uuid4())
        confirmation_num = f"RES-{res_id[:8].upper()}"
        now = datetime.now(timezone.utc)

        return Reservation(
            id=res_id,
            student_id=student_id,
            restaurant_id=str(request.restaurant_id),
            time_slot_id=str(request.time_slot_id),
            date=request.date,
            status=ReservationStatus.CONFIRMED,
            total_price=total_price,
            confirmation_number=confirmation_num,
            qr_code_path=f"/qrcodes/{res_id}.png",
            created_at=now,
            updated_at=now,
        )

    async def _persist_reservation_items(self, reservation_id: str, items: List[ReservationItemEntity]) -> None:
        for item in items:
            item.reservation_id = reservation_id
            await self._reservation_item_repo.create(item)

    @classmethod
    def _map_to_response_dto(
        cls, reservation: Reservation, reservation_id: str, items: List[ReservationItemEntity]
    ) -> ReservationResponseDTO:
        item_dtos = [cls._map_item_to_dto(item) for item in items]
        status_val = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )

        return ReservationResponseDTO(
            id=reservation_id,
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