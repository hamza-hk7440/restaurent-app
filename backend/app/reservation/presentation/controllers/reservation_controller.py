from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException

from reservation.application.dtos.availability_dtos import AvailbleDaysResponseDTO, TimeSlotResponseDTO
from reservation.application.dtos.catalog_and_menu_dtos import CreateMealCommand, CreateRestaurantCommand, CreateTimeSlotCommand, DailyMenuResponseDTO, MealResponseDTO, ManageDailyMenuCommand, RestockMealCommand, RestockMealResponseDTO, RestaurentResponseDTO, UpsertDailyMenuMealCommand, UpsertDailyMenuMealResponseDTO
from reservation.application.dtos.payment_and_notification_dtos import (
    MarkNotificationReadCommand,
    NotificationResponseDTO,
    PaginatedNotificationsResponseDTO,
    ProcessPaymentWebhookCommand,
    SendScheduledRemindersCommand,
    SendScheduledRemindersResponseDTO,
)
from reservation.application.dtos.reservation_request_dtos import (
    CancelReservationRequestDTO,
    CreateReservationLockCommand,
    CreateReservationRequestDTO,
    MarkReservationCompletedCommand,
    MarkReservationNoShowCommand,
    ModifyReservationRequestDTO,
    ReservationLockResponseDTO,
)
from reservation.application.dtos.reservation_response_dtos import (
    CancelReservationResponseDTO,
    ReservationResponseDTO,
    ReservationSummaryDTO,
)
from reservation.domain.entities.notification_entity import Notification
from reservation.domain.entities.transaction_entity import Transaction
from reservation.domain.exceptions.domain_exceptions import (
    DoubleBookingException,
    InsufficientMealStockException,
    MenuNotFoundException,
    NotificationNotFoundException,
    ReservationCancellationNotAllowedException,
    ReservationModificationNotAllowedException,
    ReservationNotFoundException,
    RestaurantNotFoundException,
    TimeSlotFullException,
    UnauthorizedAccessException,
)
from reservation.domain.value_objects.meal_availability import MealAvailability
from reservation.domain.value_objects.notification_status import NotificationStatus
from reservation.domain.value_objects.notification_type import NotificationType
from reservation.domain.value_objects.reservation_modification_type import ReservationModificationType
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.value_objects.restaurent_status import RestaurentStatus
from reservation.domain.value_objects.transaction_status import TransactionStatus
from reservation.domain.value_objects.transaction_type import TransactionType
from reservation.infrastructure.database.models import (
    DailyMenuModel,
    MealAvailabilityModel,
    RestaurantModel,
    MealModel,
    TimeSlotModel,
    NotificationModel,
    PaymentTransactionModel,
    ReservationItemModel,
    ReservationModificationModel,
    ReservationModel,
    TimeSlotAvailabilityModel,
)


@dataclass(frozen=True)
class _ReservationItemPlan:
    meal_id: str
    quantity: int
    unit_price: float
    meal_name: str
    meal_availability_id: str | None = None


class ReservationController:
    def __init__(
        self,
        restaurant_repository,
        time_slot_repository,
        daily_menu_repository,
        meal_repository,
        meal_availability_repository,
        time_slot_availability_repository,
        reservation_repository,
        reservation_item_repository,
        reservation_modification_repository,
        notification_repository,
        payment_transaction_repository,
    ):
        self._restaurant_repo = restaurant_repository
        self._time_slot_repo = time_slot_repository
        self._daily_menu_repo = daily_menu_repository
        self._meal_repo = meal_repository
        self._meal_availability_repo = meal_availability_repository
        self._time_slot_availability_repo = time_slot_availability_repository
        self._reservation_repo = reservation_repository
        self._reservation_item_repo = reservation_item_repository
        self._reservation_modification_repo = reservation_modification_repository
        self._notification_repo = notification_repository
        self._payment_transaction_repo = payment_transaction_repository

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _generate_confirmation_number(reservation_id: str) -> str:
        return f"RES-{reservation_id[:8].upper()}"

    async def list_restaurants(self, establishment_id: UUID, status_filter: RestaurentStatus | None = None):
        restaurants = await self._restaurant_repo.get_by_establishment(str(establishment_id), status_filter)
        return [RestaurentResponseDTO.from_entity(item) for item in restaurants]

    async def get_restaurant(self, restaurent_id: UUID):
        restaurant = await self._restaurant_repo.get_by_id(str(restaurent_id))
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurent_id} not found.")
        return RestaurentResponseDTO.from_entity(restaurant)

    async def get_daily_menu(self, restaurent_id: UUID, date: datetime, category: str | None = None, search_query: str | None = None):
        menu = await self._daily_menu_repo.get_by_restaurent_by_date(restaurent_id=str(restaurent_id), date=date)
        if not menu:
            raise MenuNotFoundException("Daily menu not found")
        meals = []
        for meal in menu.meals:
            if category and str(meal.category).lower() != category.lower():
                continue
            if search_query and search_query.lower() not in meal.name.lower() and search_query.lower() not in meal.description.lower():
                continue
            meals.append(MealResponseDTO.from_entity(meal))
        return DailyMenuResponseDTO(id=menu.id, restaurant_id=menu.restaurant_id, date=menu.date, is_available=menu.is_available, meals=meals)

    async def get_available_days(self, restaurent_id: UUID, start_date: datetime | None = None, days_ahead: int = 7) -> AvailbleDaysResponseDTO:
        restaurant = await self._restaurant_repo.get_by_id(str(restaurent_id))
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurent_id} not found.")
        start = (start_date or self._utcnow()).date()
        end = start + timedelta(days=days_ahead - 1)
        menus = await self._daily_menu_repo.get_by_restaurent_and_date_range(restaurent_id=str(restaurent_id), start_date=start, end_date=end)
        active_dates = {menu.date.date() if isinstance(menu.date, datetime) else menu.date for menu in menus if menu.is_available}
        is_open = restaurant.status == RestaurentStatus.OPEN
        dates = []
        day_names = []
        is_available = []
        is_operating_day = []
        for index in range(days_ahead):
            current_date = start + timedelta(days=index)
            dates.append(current_date)
            day_names.append(current_date.strftime("%A"))
            is_available.append(is_open and current_date >= self._utcnow().date() and current_date in active_dates)
            is_operating_day.append(is_open)
        return AvailbleDaysResponseDTO(date=dates, day_names=day_names, is_available=is_available, is_operating_day=is_operating_day)

    async def create_restaurant(self, command: CreateRestaurantCommand) -> RestaurentResponseDTO:
        restaurant = RestaurantModel(
            establishment_id=str(command.establishment_id),
            name=command.name,
            address=command.address,
            phone=command.phone,
            opening_time=command.opening_time,
            closing_time=command.closing_time,
            capacity=command.capacity,
            status=command.status,
            created_at=self._utcnow(),
            updated_at=self._utcnow(),
        )
        await self._restaurant_repo.create(restaurant)
        saved = await self._restaurant_repo.get_by_id(str(restaurant.id))
        return RestaurentResponseDTO.from_entity(saved)

    async def create_meal(self, command: CreateMealCommand) -> MealResponseDTO:
        await self._ensure_restaurant_exists(str(command.restaurant_id))
        meal = MealModel(
            restaurant_id=str(command.restaurant_id),
            name=command.name,
            description=command.description,
            price=command.price,
            category=command.category,
            availability_status=command.availability_status,
            meal_code=command.meal_code,
            photo_url=command.photo_url,
            rating=command.rating,
            popularity_score=command.popularity_score,
            created_at=self._utcnow(),
            updated_at=self._utcnow(),
        )
        await self._meal_repo.create(meal)
        saved = await self._meal_repo.get_by_id(str(meal.id))
        await self._sync_new_meal_with_existing_menus(str(command.restaurant_id), str(saved.id))
        return MealResponseDTO.from_entity(saved)

    async def create_time_slot(self, command: CreateTimeSlotCommand) -> TimeSlotResponseDTO:
        await self._ensure_restaurant_exists(str(command.restaurant_id))
        time_slot = TimeSlotModel(
            restaurant_id=str(command.restaurant_id),
            start_time=command.start_time,
            end_time=command.end_time,
            capacity=command.capacity,
            created_at=self._utcnow(),
        )
        await self._time_slot_repo.create(time_slot)
        saved = await self._time_slot_repo.get_by_id(str(time_slot.id))
        return TimeSlotResponseDTO.from_entity(saved)

    async def get_available_time_slots(self, restaurent_id: UUID, date: datetime):
        restaurant = await self._restaurant_repo.get_by_id(str(restaurent_id))
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurent_id} not found.")
        time_slots = await self._time_slot_repo.get_by_restaurent(str(restaurent_id))
        availabilities = await self._time_slot_availability_repo.get_available_slots(restaurent_id=str(restaurent_id), date=date)
        available_ids = {slot.time_slot_id for slot in availabilities}
        return [TimeSlotResponseDTO.from_entity(slot) for slot in time_slots if str(slot.id) in available_ids]

    async def create_reservation_lock(self, command: CreateReservationLockCommand) -> ReservationLockResponseDTO:
        await self._ensure_no_double_booking(command.student_id, command.date, str(command.time_slot_id))
        await self._ensure_restaurant_exists(str(command.restaurent_id))
        await self._ensure_time_slot_capacity(str(command.restaurent_id), str(command.time_slot_id), command.date)
        await self._ensure_menu_and_stock(str(command.restaurent_id), command.date, command.items)
        expires_at = self._utcnow() + timedelta(minutes=2)
        reservation_id = str(uuid4())
        reservation = ReservationModel(
            id=reservation_id,
            student_id=str(command.student_id),
            restaurant_id=str(command.restaurent_id),
            date=command.date,
            time_slot_id=str(command.time_slot_id),
            status=ReservationStatus.PENDING,
            total_price=0,
            confirmation_number=self._generate_confirmation_number(reservation_id),
            qr_code_path="",
            created_at=self._utcnow(),
            modified_at=self._utcnow(),
            canceled_at=None,
            completed_at=None
        )
        await self._reservation_repo.create(reservation)
        menu = await self._daily_menu_repo.get_by_restaurent_by_date(restaurent_id=str(command.restaurent_id), date=command.date)
        total_price, meal_plans = await self._build_item_plans(menu, command.items)
        reservation.total_price = total_price
        await self._reservation_repo.update(reservation)
        await self._reserve_inventory(str(command.time_slot_id), command.date, meal_plans)
        for plan in meal_plans:
            await self._reservation_item_repo.create(
                ReservationItemModel(
                    reservation_id=reservation_id,
                    meal_id=plan.meal_id,
                    quantity=plan.quantity,
                    unit_price=plan.unit_price,
                    subtotal=plan.unit_price * plan.quantity,
                )
            )
        return ReservationLockResponseDTO(lock_id=reservation_id, student_id=command.student_id, restaurent_id=command.restaurent_id, time_slot_id=command.time_slot_id, expires_at=expires_at, is_active=True)

    async def create_reservation(self, request: CreateReservationRequestDTO, student_id: UUID) -> ReservationResponseDTO:
        await self._ensure_restaurant_exists(str(request.restaurent_id))
        await self._ensure_time_slot_capacity(str(request.restaurent_id), str(request.time_slot_id), request.date)
        menu = await self._resolve_daily_menu(request.restaurent_id, request.date)
        total_price, meal_plans = await self._build_item_plans(menu, request.items)
        existing_lock = await self._find_pending_reservation(student_id, request.date, str(request.time_slot_id))
        if existing_lock:
            await self._release_reservation_inventory(existing_lock)
            for existing_item in list(existing_lock.items):
                await self._reservation_item_repo.delete(str(existing_item.id))
            reservation = existing_lock
            reservation.status = ReservationStatus.CONFIRMED
            reservation.total_price = total_price
            reservation.qr_code_path = f"/qrcodes/{reservation.id}.png"
            reservation.updated_at = self._utcnow()
            await self._reservation_repo.update(reservation)
            await self._reserve_inventory(str(request.time_slot_id), request.date, meal_plans)
        else:
            await self._ensure_no_double_booking(student_id, request.date, str(request.time_slot_id))
            reservation_id = str(uuid4())
            reservation = ReservationModel(
                id=reservation_id,
                student_id=str(student_id),
                restaurant_id=str(request.restaurent_id),
                date=request.date,
                time_slot_id=str(request.time_slot_id),
                status=ReservationStatus.CONFIRMED,
                total_price=total_price,
                confirmation_number=self._generate_confirmation_number(reservation_id),
                qr_code_path=f"/qrcodes/{reservation_id}.png",
                created_at=self._utcnow(),
                updated_at=self._utcnow(),
            )
            await self._reservation_repo.create(reservation)
            await self._reserve_inventory(str(request.time_slot_id), request.date, meal_plans)
        for plan in meal_plans:
            await self._reservation_item_repo.create(
                ReservationItemModel(
                    reservation_id=str(reservation.id),
                    meal_id=plan.meal_id,
                    quantity=plan.quantity,
                    unit_price=plan.unit_price,
                    subtotal=plan.unit_price * plan.quantity,
                )
            )
        stored_reservation = await self._reservation_repo.get_by_id(str(reservation.id))
        return ReservationResponseDTO.from_entity(stored_reservation)

    async def get_reservation_details(self, reservation_id: UUID, student_id: UUID) -> ReservationResponseDTO:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        if str(reservation.student_id) != str(student_id):
            raise UnauthorizedAccessException("You are not authorized to access this reservation.")
        return ReservationResponseDTO.from_entity(reservation)

    async def get_reservation_admin(self, reservation_id: UUID) -> ReservationResponseDTO:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        return ReservationResponseDTO.from_entity(reservation)

    async def list_student_reservations(self, student_id: UUID, filter_type: str = "UPCOMING"):
        if filter_type.upper() == "HISTORY":
            reservations = await self._reservation_repo.get_reservation_history(str(student_id))
        elif filter_type.upper() == "UPCOMING":
            reservations = await self._reservation_repo.get_upcoming_reservations(str(student_id))
        else:
            reservations = await self._reservation_repo.get_by_student_id(str(student_id))
        return [ReservationSummaryDTO.from_entity(item) for item in reservations]

    async def modify_reservation(self, reservation_id: UUID, student_id: UUID, request: ModifyReservationRequestDTO) -> ReservationResponseDTO:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        if str(reservation.student_id) != str(student_id):
            raise UnauthorizedAccessException("You are not authorized to modify this reservation.")
        if reservation.status in {ReservationStatus.CANCELLED, ReservationStatus.COMPLETED}:
            raise ReservationModificationNotAllowedException("Reservation can no longer be modified.")

        if request.new_time_slot_id and str(request.new_time_slot_id) != str(reservation.time_slot_id):
            current_slot = await self._time_slot_availability_repo.get_by_slot_date(str(reservation.time_slot_id), reservation.date)
            if current_slot:
                await self._time_slot_availability_repo.release_slot(str(current_slot.id), 1)
            has_double = await self._reservation_repo.check_double_booking(str(student_id), request.date or reservation.date, str(request.new_time_slot_id))
            if has_double:
                raise DoubleBookingException("Student already has an active reservation for the target time slot.")
            await self._ensure_time_slot_capacity(str(reservation.restaurant_id), str(request.new_time_slot_id), reservation.date)
            new_slot = await self._time_slot_availability_repo.get_by_slot_date(str(request.new_time_slot_id), reservation.date)
            if new_slot:
                await self._time_slot_availability_repo.reserve_slot(str(new_slot.id), 1)
            reservation.time_slot_id = str(request.new_time_slot_id)

        if request.new_items is not None:
            menu = await self._resolve_daily_menu(UUID(str(reservation.restaurant_id)), reservation.date)
            await self._release_meals(reservation)
            total_price, meal_plans = await self._build_item_plans(menu, request.new_items)
            reservation.total_price = total_price
            for existing_item in list(reservation.items):
                await self._reservation_item_repo.delete(str(existing_item.id))
            for plan in meal_plans:
                await self._reservation_item_repo.create(
                    ReservationItemModel(
                        reservation_id=str(reservation.id),
                        meal_id=plan.meal_id,
                        quantity=plan.quantity,
                        unit_price=plan.unit_price,
                        subtotal=plan.unit_price * plan.quantity,
                    )
                )
            await self._reserve_meals(menu.id, meal_plans)
            await self._reservation_modification_repo.create(
                ReservationModificationModel(
                    reservation_id=str(reservation.id),
                    modification_type=ReservationModificationType.MEAL,
                    old_value="items changed",
                    new_value="items updated",
                    price_adjustment=0,
                )
            )

        reservation.updated_at = self._utcnow()
        await self._reservation_repo.update(reservation)
        updated = await self._reservation_repo.get_by_id(str(reservation_id))
        return ReservationResponseDTO.from_entity(updated)

    async def manage_daily_menu(self, command: ManageDailyMenuCommand) -> DailyMenuResponseDTO:
        await self._ensure_restaurant_exists(str(command.restaurant_id))
        menu = await self._daily_menu_repo.get_by_restaurent_by_date(restaurent_id=str(command.restaurant_id), date=command.target_date)
        if not menu:
            menu = DailyMenuModel(
                restaurant_id=str(command.restaurant_id),
                date=command.target_date,
                is_available=command.is_available,
                notes=command.notes,
                created_at=self._utcnow(),
                updated_at=self._utcnow(),
            )
            await self._daily_menu_repo.create(menu)
        else:
            menu.is_available = command.is_available
            menu.notes = command.notes
            menu.updated_at = self._utcnow()
            await self._daily_menu_repo.update(menu)
        await self._sync_menu_with_restaurant_meals(str(menu.id), str(command.restaurant_id))
        saved_menu = await self._daily_menu_repo.get_by_id(str(menu.id))
        return DailyMenuResponseDTO.from_entity(saved_menu)

    async def restock_meal(self, command: RestockMealCommand) -> RestockMealResponseDTO:
        menu = await self._daily_menu_repo.get_by_id(str(command.menu_id))
        if not menu:
            raise MenuNotFoundException(f"Daily menu with ID '{command.menu_id}' not found.")
        if command.restaurant_id and str(menu.restaurant_id) != str(command.restaurant_id):
            raise RestaurantNotFoundException(f"Menu '{command.menu_id}' does not belong to restaurant '{command.restaurant_id}'.")
        previous_quantity = int(getattr(menu, "stored_available_quantity", getattr(menu, "available_quantity", 0)))
        menu.stored_available_quantity = previous_quantity + command.quantity_to_add
        menu.updated_at = self._utcnow()
        await self._daily_menu_repo.update(menu)
        meal_availabilities = await self._meal_availability_repo.get_by_daily_menu(str(menu.id))
        for meal_availability in meal_availabilities:
            meal_availability.quantity_available = int(getattr(meal_availability, "quantity_available", 0)) + command.quantity_to_add
            meal_availability.updated_at = self._utcnow()
            await self._meal_availability_repo.update(meal_availability)
        return RestockMealResponseDTO(
            menu_id=menu.id,
            restaurant_id=menu.restaurant_id,
            previous_quantity=previous_quantity,
            new_quantity=int(getattr(menu, "stored_available_quantity", previous_quantity)),
            updated_at=menu.updated_at,
        )

    async def upsert_daily_menu_meal(self, command: UpsertDailyMenuMealCommand) -> UpsertDailyMenuMealResponseDTO:
        menu = await self._daily_menu_repo.get_by_id(str(command.daily_menu_id))
        if not menu:
            raise MenuNotFoundException(f"Daily menu with ID '{command.daily_menu_id}' not found.")

        meal = await self._meal_repo.get_by_id(str(command.meal_id))
        if not meal:
            raise MenuNotFoundException(f"Meal with ID '{command.meal_id}' not found.")
        if str(meal.restaurant_id) != str(menu.restaurant_id):
            raise RestaurantNotFoundException(
                f"Meal '{command.meal_id}' does not belong to restaurant '{menu.restaurant_id}'."
            )

        meal_availability = await self._meal_availability_repo.get_by_daily_menu_meal(
            str(menu.id), str(command.meal_id)
        )
        if meal_availability:
            meal_availability.quantity_available = command.quantity_available
            meal_availability.updated_at = self._utcnow()
            await self._meal_availability_repo.update(meal_availability)
        else:
            meal_availability = MealAvailabilityModel(
                daily_menu_id=str(menu.id),
                meal_id=str(command.meal_id),
                quantity_available=command.quantity_available,
                quantity_reserved=0,
            )
            await self._meal_availability_repo.create(meal_availability)

        saved = await self._meal_availability_repo.get_by_daily_menu_meal(str(menu.id), str(command.meal_id))
        return UpsertDailyMenuMealResponseDTO(
            daily_menu_id=saved.daily_menu_id,
            meal_id=saved.meal_id,
            quantity_available=saved.quantity_available,
            quantity_reserved=saved.quantity_reserved,
            remaining_quantity=saved.remaining_quantity,
            is_sold_out=saved.is_sold_out,
        )

    async def cancel_reservation(self, reservation_id: UUID, student_id: UUID, request: CancelReservationRequestDTO | None = None) -> CancelReservationResponseDTO:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        if str(reservation.student_id) != str(student_id):
            raise UnauthorizedAccessException("You are not authorized to cancel this reservation.")
        if reservation.status == ReservationStatus.CANCELLED:
            raise ReservationCancellationNotAllowedException("Reservation is already cancelled.")
        if reservation.status == ReservationStatus.COMPLETED:
            raise ReservationCancellationNotAllowedException("Cannot cancel a completed reservation.")
        await self._release_reservation_inventory(reservation)
        await self._reservation_repo.cancel(str(reservation_id))
        return CancelReservationResponseDTO(reservation_id=reservation_id, status=ReservationStatus.CANCELLED, message=(request.reason if request and request.reason else "Reservation cancelled successfully."))

    async def cancel_reservation_admin(self, reservation_id: UUID, reason: str | None = None) -> CancelReservationResponseDTO:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        if reservation.status == ReservationStatus.CANCELLED:
            raise ReservationCancellationNotAllowedException("Reservation is already cancelled.")
        if reservation.status == ReservationStatus.COMPLETED:
            raise ReservationCancellationNotAllowedException("Cannot cancel a completed reservation.")
        await self._release_reservation_inventory(reservation)
        await self._reservation_repo.cancel(str(reservation_id))
        return CancelReservationResponseDTO(
            reservation_id=reservation_id,
            status=ReservationStatus.CANCELLED,
            message=reason or "Reservation cancelled successfully.",
        )

    async def list_notifications(self, student_id: UUID, limit: int = 50, offset: int = 0, status_filter: NotificationStatus | None = None):
        notifications = await self._notification_repo.get_by_student_id(str(student_id), limit=limit, offset=offset, status=status_filter)
        total = await self._notification_repo.count_by_student_id(str(student_id), status=status_filter)
        return PaginatedNotificationsResponseDTO(items=[NotificationResponseDTO.from_entity(item) for item in notifications], total=total, limit=limit, offset=offset)

    async def mark_notification_read(self, notification_id: UUID, student_id: UUID | None = None) -> NotificationResponseDTO:
        notification = await self._notification_repo.get_by_id(str(notification_id))
        if not notification:
            raise NotificationNotFoundException(f"Notification with ID '{notification_id}' not found.")
        if student_id and str(notification.student_id) != str(student_id):
            raise UnauthorizedAccessException("Notification does not belong to the requested student.")
        updated = await self._notification_repo.update_status(str(notification_id), NotificationStatus.READ)
        return NotificationResponseDTO.from_entity(updated)

    async def mark_reservation_completed(self, reservation_id: UUID, student_id: UUID | None = None):
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        if student_id and str(reservation.student_id) != str(student_id):
            raise UnauthorizedAccessException("You are not authorized to update this reservation.")
        await self._reservation_repo.mark_completed(str(reservation_id))
        updated = await self._reservation_repo.get_by_id(str(reservation_id))
        return ReservationResponseDTO.from_entity(updated)

    async def mark_reservation_no_show(self, reservation_id: UUID, student_id: UUID | None = None, reason: str | None = None):
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        if student_id and str(reservation.student_id) != str(student_id):
            raise UnauthorizedAccessException("You are not authorized to update this reservation.")
        reservation.status = ReservationStatus.NO_SHOW
        await self._reservation_repo.update(reservation)
        return ReservationResponseDTO.from_entity(await self._reservation_repo.get_by_id(str(reservation_id)))

    async def update_restaurant_status(self, restaurant_id: UUID, new_status: RestaurentStatus, reason: str | None = None):
        restaurant = await self._restaurant_repo.get_by_id(str(restaurant_id))
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        previous = restaurant.status
        await self._restaurant_repo.update_status(str(restaurant_id), new_status)
        return {
            "restaurant_id": restaurant_id,
            "previous_status": previous,
            "new_status": new_status,
            "message": reason or "Restaurant status updated.",
            "success": True,
        }

    async def validate_qr_code(self, reservation_id: UUID, qr_code_data: str):
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        is_valid = str(qr_code_data).strip() == str(reservation.qr_code_path).strip()
        return {
            "is_valid": is_valid,
            "reservation_id": reservation_id,
            "student_id": reservation.student_id,
            "status": reservation.status,
            "message": "QR code valid" if is_valid else "Invalid QR code",
            "validated_at": self._utcnow(),
        }

    async def send_scheduled_reminders(self, command: SendScheduledRemindersCommand) -> SendScheduledRemindersResponseDTO:
        target_date = command.target_date or self._utcnow().date()
        reservations = await self._reservation_repo.get_pending_reminders(target_date=target_date, limit=command.limit)
        notifications = []
        for reservation in reservations:
            notification = NotificationModel(
                student_id=reservation.student_id,
                reservation_id=reservation.id,
                notification_type=NotificationType.REMINDER_24H,
                title="Reservation Reminder",
                message=f"Reminder: you have a reservation for {reservation.date}.",
                status=NotificationStatus.SENT,
                sent_at=self._utcnow(),
                created_at=self._utcnow(),
            )
            await self._notification_repo.save(notification)
            await self._reservation_repo.mark_reminder_sent(str(reservation.id))
            notifications.append(NotificationResponseDTO.from_entity(notification))
        return SendScheduledRemindersResponseDTO(total_processed=len(notifications), successful_sent=len(notifications), failed_sent=0, notification=notifications)

    async def process_payment_webhook(self, command: ProcessPaymentWebhookCommand):
        transaction = PaymentTransactionModel(
            id=str(command.transaction_id),
            student_id=str(await self._get_reservation_student_id(command.reservation_id)),
            reservation_id=str(command.reservation_id),
            amount=command.amount,
            transaction_type=TransactionType.CHARGE if command.amount >= 0 else TransactionType.REFUND,
            status=TransactionStatus.SUCCESS if command.payment_status.lower() in {"paid", "success", "succeeded"} else TransactionStatus.FAILED,
            payment_method=command.payment_method,
            reference_id=command.reference_id,
            payload=str(command.payload) if command.payload is not None else None,
            created_at=self._utcnow(),
        )
        saved = await self._payment_transaction_repo.save(transaction)
        return saved

    async def _get_reservation_student_id(self, reservation_id: UUID) -> UUID:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID {reservation_id} not found.")
        return UUID(str(reservation.student_id))

    async def _ensure_restaurant_exists(self, restaurant_id: str) -> None:
        restaurant = await self._restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurant_id} not found.")

    async def _ensure_no_double_booking(self, student_id: UUID, date_value: datetime, time_slot: str) -> None:
        if await self._reservation_repo.check_double_booking(str(student_id), date_value, time_slot):
            raise DoubleBookingException("Student already has an active reservation for this time slot.")

    async def _ensure_time_slot_capacity(self, restaurant_id: str, time_slot_id: str, date_value: datetime) -> None:
        if not await self._time_slot_availability_repo.has_capacity(restaurant_id, time_slot_id, date_value):
            raise TimeSlotFullException("Selected time slot is fully booked.")

    async def _resolve_daily_menu(self, restaurent_id: UUID, date_value: datetime) -> DailyMenuModel:
        menu = await self._daily_menu_repo.get_by_restaurent_by_date(restaurent_id=str(restaurent_id), date=date_value)
        if not menu:
            raise MenuNotFoundException(f"No active menu found for date {date_value}.")
        return menu

    async def _find_pending_reservation(self, student_id: UUID, date_value: datetime, time_slot_id: str) -> ReservationModel | None:
        reservations = await self._reservation_repo.get_by_student_id(str(student_id))
        for reservation in reservations:
            if str(reservation.time_slot_id) != str(time_slot_id):
                continue
            if (reservation.date.date() if isinstance(reservation.date, datetime) else reservation.date) != (
                date_value.date() if isinstance(date_value, datetime) else date_value
            ):
                continue
            if reservation.status == ReservationStatus.PENDING:
                return reservation
        return None

    async def _ensure_menu_and_stock(self, restaurent_id: str, date_value: datetime, items) -> None:
        menu = await self._daily_menu_repo.get_by_restaurent_by_date(restaurent_id=restaurent_id, date=date_value)
        if not menu:
            raise MenuNotFoundException(f"No active menu found for date {date_value}.")
        for item in items:
            meal_availability = next((entry for entry in menu.meal_availabilities if str(entry.meal_id) == str(item.meal_id)), None)
            if not meal_availability:
                available_meals = ", ".join(
                    f"{entry.meal_id} ({entry.meal.name})"
                    for entry in menu.meal_availabilities
                    if getattr(entry, "meal", None) is not None
                ) or "none"
                raise InsufficientMealStockException(
                    f"Meal ID {item.meal_id} is not on the daily menu for {date_value.date()}. "
                    f"Available meal IDs: {available_meals}."
                )
            if meal_availability.remaining_quantity < item.quantity:
                raise InsufficientMealStockException(f"Insufficient stock for meal: {meal_availability.meal.name}.")

    async def _build_item_plans(self, daily_menu: DailyMenuModel, items) -> tuple[float, list[_ReservationItemPlan]]:
        total_price = 0.0
        plans: list[_ReservationItemPlan] = []
        for item in items:
            meal_availability = next((entry for entry in daily_menu.meal_availabilities if str(entry.meal_id) == str(item.meal_id)), None)
            if not meal_availability:
                available_meals = ", ".join(
                    f"{entry.meal_id} ({entry.meal.name})"
                    for entry in daily_menu.meal_availabilities
                    if getattr(entry, "meal", None) is not None
                ) or "none"
                raise InsufficientMealStockException(
                    f"Meal ID {item.meal_id} is not on the daily menu. "
                    f"Available meal IDs: {available_meals}."
                )
            if meal_availability.remaining_quantity < item.quantity:
                raise InsufficientMealStockException(f"Insufficient stock for meal {meal_availability.meal.name}.")
            unit_price = float(meal_availability.meal.price)
            total_price += unit_price * item.quantity
            plans.append(_ReservationItemPlan(meal_id=str(item.meal_id), quantity=item.quantity, unit_price=unit_price, meal_name=meal_availability.meal.name, meal_availability_id=str(meal_availability.id)))
        return total_price, plans

    async def _reserve_inventory(self, time_slot_id: str, date_value: datetime, meal_plans: list[_ReservationItemPlan]) -> None:
        time_slot_availability = await self._time_slot_availability_repo.get_by_slot_date(time_slot_id, date_value)
        if not time_slot_availability:
            slot = await self._time_slot_repo.get_by_id(time_slot_id)
            slot_capacity = slot.capacity if slot else 1
            created_id = await self._time_slot_availability_repo.create(
                TimeSlotAvailabilityModel(
                    time_slot_id=time_slot_id,
                    date=date_value,
                    quantity_available=slot_capacity,
                    quantity_reserved=0,
                )
            )
            time_slot_availability = await self._time_slot_availability_repo.get_by_id(created_id)
        await self._time_slot_availability_repo.reserve_slot(str(time_slot_availability.id), 1)
        for plan in meal_plans:
            if plan.meal_availability_id:
                await self._meal_availability_repo.reserve_quantity(plan.meal_availability_id, plan.quantity)

    async def _sync_menu_with_restaurant_meals(self, daily_menu_id: str, restaurant_id: str) -> None:
        menu = await self._daily_menu_repo.get_by_id(daily_menu_id)
        if not menu:
            return
        restaurant_meals = await self._meal_repo.get_by_restaurent(restaurant_id)
        existing_meal_ids = {str(item.meal_id) for item in menu.meal_availabilities}
        for meal in restaurant_meals:
            meal_id = str(meal.id)
            if meal_id in existing_meal_ids:
                continue
            await self._meal_availability_repo.create(
                MealAvailabilityModel(
                    daily_menu_id=str(menu.id),
                    meal_id=meal_id,
                    quantity_available=0,
                    quantity_reserved=0,
                )
            )

    async def _sync_new_meal_with_existing_menus(self, restaurant_id: str, meal_id: str) -> None:
        menus = await self._daily_menu_repo.get_by_restaurent_and_date_range(restaurent_id=restaurant_id)
        for menu in menus:
            existing = await self._meal_availability_repo.get_by_daily_menu_meal(str(menu.id), meal_id)
            if existing:
                continue
            await self._meal_availability_repo.create(
                MealAvailabilityModel(
                    daily_menu_id=str(menu.id),
                    meal_id=meal_id,
                    quantity_available=0,
                    quantity_reserved=0,
                )
            )

    async def _reserve_meals(self, daily_menu_id: str, meal_plans: list[_ReservationItemPlan]) -> None:
        for plan in meal_plans:
            if plan.meal_availability_id:
                await self._meal_availability_repo.reserve_quantity(plan.meal_availability_id, plan.quantity)

    async def _release_meals(self, reservation: ReservationModel) -> None:
        menu = await self._daily_menu_repo.get_by_restaurent_by_date(restaurent_id=str(reservation.restaurant_id), date=reservation.date)
        if not menu:
            return
        for item in reservation.items:
            meal_availability = await self._meal_availability_repo.get_by_daily_menu_meal(str(menu.id), str(item.meal_id))
            if meal_availability:
                await self._meal_availability_repo.release_quantity(str(meal_availability.id), item.quantity)

    async def _release_items(self, reservation: ReservationModel) -> None:
        await self._release_reservation_inventory(reservation)

    async def _release_reservation_inventory(self, reservation: ReservationModel) -> None:
        time_slot_availability = await self._time_slot_availability_repo.get_by_slot_date(reservation.time_slot_id, reservation.date)
        if time_slot_availability:
            await self._time_slot_availability_repo.release_slot(str(time_slot_availability.id), 1)
        await self._release_meals(reservation)
