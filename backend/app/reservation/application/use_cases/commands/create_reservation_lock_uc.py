from datetime import datetime, timedelta, timezone
from typing import List
from uuid import uuid4

from reservation.domain.entities.reservation_entity import Reservation
from reservation.domain.entities.reservation_item_entity import ReservationItemEntity
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.interfaces.restaurent_repo import IRestaurentRepository
from reservation.domain.interfaces.time_slot_availability_repo import ITimeSlotAvailabilityRepository
from reservation.domain.interfaces.daily_menu_repo import IDailyMenuRepository
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.domain.interfaces.reservation_item_repo import IReservationItemRepository
from reservation.domain.exceptions.domain_exceptions import (
    RestaurantNotFoundException,
    TimeSlotFullException,
    InsufficientMealStockException,
    MenuNotFoundException,
    DoubleBookingException,
)
from reservation.application.dtos.reservation_request_dtos import (
    CreateReservationLockCommand,
    ReservationLockResponseDTO,
)
class CreateReservationLockUseCase:
    LOCK_DURATION_MINUTES = 2

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

    async def execute(self, command: CreateReservationLockCommand) -> ReservationLockResponseDTO:
        await self._ensure_no_double_booking(command.student_id, command.date, str(command.time_slot_id))
        await self._ensure_restaurant_exists(str(command.restaurant_id))
        await self._verify_time_slot_capacity(str(command.restaurant_id), str(command.time_slot_id), command.date)
        await self._verify_meals_stock(str(command.restaurant_id), command.date, command.items)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.LOCK_DURATION_MINUTES)
        
        pending_reservation = self._build_pending_reservation(command, expires_at)
        reservation_id = await self._reservation_repo.create(pending_reservation)

        await self._create_reservation_items(reservation_id, command.items)

        return self._map_to_response_dto(pending_reservation, reservation_id, expires_at)

    async def _ensure_no_double_booking(self, student_id: str, lock_date: datetime, time_slot: str) -> None:
        has_double_booking = await self._reservation_repo.check_double_booking(
            student_id=str(student_id),
            date=lock_date,
            time_slot=time_slot,
        )
        if has_double_booking:
            raise DoubleBookingException("Student already has an active reservation for this time slot.")

    async def _ensure_restaurant_exists(self, restaurant_id: str) -> None:
        restaurant = await self._restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurant_id} not found.")

    async def _verify_time_slot_capacity(self, restaurant_id: str, time_slot_id: str, lock_date: datetime) -> None:
        is_available = await self._time_slot_availability_repo.has_capacity(
            restaurant_id=restaurant_id,
            time_slot_id=time_slot_id,
            date=lock_date,
        )
        if not is_available:
            raise TimeSlotFullException("Selected time slot is fully booked.")

    async def _verify_meals_stock(self, restaurant_id: str, lock_date: datetime, items: list) -> None:
        menu = await self._daily_menu_repo.get_by_restaurant_and_date(restaurant_id, lock_date)
        if not menu:
            raise MenuNotFoundException(f"No active menu found for date {lock_date}.")

        for item in items:
            self._check_single_item_stock(menu, str(item.meal_id), item.quantity)

    @staticmethod
    def _check_single_item_stock(menu, meal_id: str, requested_qty: int) -> None:
        meal = next((m for m in menu.meals if str(m.id) == meal_id), None)
        if not meal:
            raise InsufficientMealStockException(f"Meal ID {meal_id} is not in today's menu.")

        available_qty = getattr(meal, "quantity_available", 0)
        if available_qty < requested_qty:
            raise InsufficientMealStockException(f"Insufficient stock for meal: {getattr(meal, 'name', meal_id)}.")

    @staticmethod
    def _build_pending_reservation(command: CreateReservationLockCommand, expires_at: datetime) -> Reservation:
        return Reservation(
            id=str(uuid4()),
            student_id=str(command.student_id),
            restaurant_id=str(command.restaurant_id),
            time_slot_id=str(command.time_slot_id),
            date=command.date,
            status=ReservationStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def _create_reservation_items(self, reservation_id: str, items: list) -> None:
        for item in items:
            item_entity = ReservationItemEntity(
                id=str(uuid4()),
                reservation_id=reservation_id,
                meal_id=str(item.meal_id),
                quantity=item.quantity,
            )
            await self._reservation_item_repo.create(item_entity)

    @staticmethod
    def _map_to_response_dto(
        reservation: Reservation,
        reservation_id: str,
        expires_at: datetime
    ) -> ReservationLockResponseDTO:
        return ReservationLockResponseDTO(
            lock_id=reservation_id,
            student_id=reservation.student_id,
            restaurant_id=reservation.restaurant_id,
            time_slot_id=reservation.time_slot_id,
            expires_at=expires_at,
            is_active=True,
        )