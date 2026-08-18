from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from reservation.domain.value_objects.meal_availability import MealAvailability
from reservation.domain.value_objects.meal_category import MealCategory
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
    MealModel,
    NotificationModel,
    PaymentTransactionModel,
    ReservationItemModel,
    ReservationModificationModel,
    ReservationModel,
    RestaurantModel,
    TimeSlotAvailabilityModel,
    TimeSlotModel,
)


def _as_str(value) -> str:
    return str(value) if value is not None else ""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _enum_value(value):
    if hasattr(value, "value"):
        return value.value
    return value


def _copy_fields(target, source, fields: Iterable[str]) -> None:
    for field in fields:
        if hasattr(source, field):
            setattr(target, field, getattr(source, field))


class _RepositoryBase:
    def __init__(self, session: AsyncSession):
        self.session = session


class RestaurantRepository(_RepositoryBase):
    async def create(self, restaurent) -> str:
        model = restaurent if isinstance(restaurent, RestaurantModel) else RestaurantModel()
        if model is not restaurent:
            _copy_fields(
                model,
                restaurent,
                ["id", "establishment_id", "name", "address", "phone", "opening_time", "closing_time", "capacity", "status"],
            )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def get_by_id(self, restaurent_id: str) -> Optional[RestaurantModel]:
        result = await self.session.execute(select(RestaurantModel).where(RestaurantModel.id == _as_str(restaurent_id)))
        return result.scalar_one_or_none()

    async def get_by_establishment(self, establishment_id: str, status: RestaurentStatus | None = None) -> list[RestaurantModel]:
        statement = select(RestaurantModel).where(RestaurantModel.establishment_id == _as_str(establishment_id))
        if status is not None:
            statement = statement.where(RestaurantModel.status == status)
        result = await self.session.execute(statement.order_by(RestaurantModel.name.asc()))
        return list(result.scalars().all())

    async def get_all(self) -> list[RestaurantModel]:
        result = await self.session.execute(select(RestaurantModel).order_by(RestaurantModel.name.asc()))
        return list(result.scalars().all())

    async def update(self, restaurent) -> str:
        model = restaurent if isinstance(restaurent, RestaurantModel) else await self.get_by_id(getattr(restaurent, "id"))
        if not model:
            return ""
        if model is not restaurent:
            _copy_fields(
                model,
                restaurent,
                ["name", "address", "phone", "opening_time", "closing_time", "capacity", "status"],
            )
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def delete(self, restaurent_id: str) -> str:
        await self.session.execute(delete(RestaurantModel).where(RestaurantModel.id == _as_str(restaurent_id)))
        await self.session.commit()
        return _as_str(restaurent_id)

    async def get_by_name(self, name: str) -> Optional[RestaurantModel]:
        result = await self.session.execute(select(RestaurantModel).where(RestaurantModel.name == name))
        return result.scalar_one_or_none()

    async def get_open_restaurants(self) -> list[RestaurantModel]:
        result = await self.session.execute(select(RestaurantModel).where(RestaurantModel.status == RestaurentStatus.OPEN).order_by(RestaurantModel.name.asc()))
        return list(result.scalars().all())

    async def update_status(self, restaurent_id: str, status: RestaurentStatus) -> str:
        model = await self.get_by_id(restaurent_id)
        if not model:
            return ""
        model.status = status
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id


class TimeSlotRepository(_RepositoryBase):
    async def create(self, time_slot) -> str:
        model = time_slot if isinstance(time_slot, TimeSlotModel) else TimeSlotModel()
        if model is not time_slot:
            _copy_fields(model, time_slot, ["id", "restaurant_id", "start_time", "end_time", "capacity"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def get_by_id(self, time_slot_id: str) -> Optional[TimeSlotModel]:
        result = await self.session.execute(select(TimeSlotModel).where(TimeSlotModel.id == _as_str(time_slot_id)))
        return result.scalar_one_or_none()

    async def get_by_restaurent(self, restaurent_id: str) -> list[TimeSlotModel]:
        result = await self.session.execute(select(TimeSlotModel).where(TimeSlotModel.restaurant_id == _as_str(restaurent_id)).order_by(TimeSlotModel.start_time.asc()))
        return list(result.scalars().all())

    async def get_by_restaurent_time(self, restaurent_id: str, time: datetime) -> Optional[TimeSlotModel]:
        result = await self.session.execute(
            select(TimeSlotModel).where(TimeSlotModel.restaurant_id == _as_str(restaurent_id), TimeSlotModel.start_time <= time, TimeSlotModel.end_time >= time)
        )
        return result.scalar_one_or_none()

    async def get_active_slots(self, restaurent_id: str) -> list[TimeSlotModel]:
        result = await self.session.execute(
            select(TimeSlotModel)
            .join(TimeSlotAvailabilityModel, TimeSlotAvailabilityModel.time_slot_id == TimeSlotModel.id)
            .where(TimeSlotModel.restaurant_id == _as_str(restaurent_id), TimeSlotAvailabilityModel.quantity_available > TimeSlotAvailabilityModel.quantity_reserved)
            .order_by(TimeSlotModel.start_time.asc())
        )
        return list(result.scalars().unique().all())

    async def update(self, time_slot) -> str:
        model = time_slot if isinstance(time_slot, TimeSlotModel) else await self.get_by_id(getattr(time_slot, "id"))
        if not model:
            return ""
        if model is not time_slot:
            _copy_fields(model, time_slot, ["restaurant_id", "start_time", "end_time", "capacity"])
        await self.session.commit()
        return model.id

    async def delete(self, time_slot_id: str) -> str:
        await self.session.execute(delete(TimeSlotModel).where(TimeSlotModel.id == _as_str(time_slot_id)))
        await self.session.commit()
        return _as_str(time_slot_id)

    async def activate_slot(self, time_slot_id: str) -> str:
        model = await self.get_by_id(time_slot_id)
        if model is None:
            return ""
        await self.session.commit()
        return model.id

    async def deactivate_slot(self, time_slot_id: str) -> str:
        model = await self.get_by_id(time_slot_id)
        if model is None:
            return ""
        await self.session.commit()
        return model.id


class MealRepository(_RepositoryBase):
    async def create(self, meal) -> str:
        model = meal if isinstance(meal, MealModel) else MealModel()
        if model is not meal:
            _copy_fields(model, meal, ["id", "restaurant_id", "name", "description", "price", "category", "availability_status", "meal_code", "photo_url", "rating", "popularity_score"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def get_by_id(self, meal_id: str) -> Optional[MealModel]:
        result = await self.session.execute(select(MealModel).where(MealModel.id == _as_str(meal_id)))
        return result.scalar_one_or_none()

    async def get_by_code(self, meal_code: str) -> Optional[MealModel]:
        result = await self.session.execute(select(MealModel).where(MealModel.meal_code == meal_code))
        return result.scalar_one_or_none()

    async def get_by_category(self, category: MealCategory) -> list[MealModel]:
        result = await self.session.execute(select(MealModel).where(MealModel.category == category).order_by(MealModel.name.asc()))
        return list(result.scalars().all())

    async def get_by_restaurent(self, restaurent_id: str) -> list[MealModel]:
        result = await self.session.execute(select(MealModel).where(MealModel.restaurant_id == _as_str(restaurent_id)).order_by(MealModel.name.asc()))
        return list(result.scalars().all())

    async def search_by_name(self, name: str) -> list[MealModel]:
        result = await self.session.execute(select(MealModel).where(MealModel.name.ilike(f"%{name}%")))
        return list(result.scalars().all())

    async def get_available_meals(self) -> list[MealModel]:
        result = await self.session.execute(select(MealModel).where(MealModel.availability_status == MealAvailability.AVAILABLE))
        return list(result.scalars().all())

    async def get_by_rating(self, min_rating: float) -> list[MealModel]:
        result = await self.session.execute(select(MealModel).where(MealModel.rating >= min_rating))
        return list(result.scalars().all())

    async def get_by_popularity(self, min_popularity: float) -> list[MealModel]:
        result = await self.session.execute(select(MealModel).where(MealModel.popularity_score >= min_popularity))
        return list(result.scalars().all())

    async def update(self, meal) -> str:
        model = meal if isinstance(meal, MealModel) else await self.get_by_id(getattr(meal, "id"))
        if not model:
            return ""
        if model is not meal:
            _copy_fields(model, meal, ["restaurant_id", "name", "description", "price", "category", "availability_status", "meal_code", "photo_url", "rating", "popularity_score"])
        await self.session.commit()
        return model.id

    async def delete(self, meal_id: str) -> str:
        await self.session.execute(delete(MealModel).where(MealModel.id == _as_str(meal_id)))
        await self.session.commit()
        return _as_str(meal_id)

    async def update_availability(self, meal_id: str, availability_status: MealAvailability) -> str:
        model = await self.get_by_id(meal_id)
        if model is None:
            return ""
        model.availability_status = availability_status
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id


class DailyMenuRepository(_RepositoryBase):
    async def create(self, daily_menu) -> str:
        model = daily_menu if isinstance(daily_menu, DailyMenuModel) else DailyMenuModel()
        if model is not daily_menu:
            _copy_fields(model, daily_menu, ["id", "restaurant_id", "date", "is_available", "created_by", "stored_available_quantity"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def get_by_id(self, daily_menu_id: str) -> Optional[DailyMenuModel]:
        result = await self.session.execute(
            select(DailyMenuModel)
            .options(selectinload(DailyMenuModel.meal_availabilities).selectinload(MealAvailabilityModel.meal))
            .where(DailyMenuModel.id == _as_str(daily_menu_id))
        )
        return result.scalar_one_or_none()

    async def get_by_restaurent_and_date_range(self, restaurent_id: str | None = None, start_date: datetime | None = None, end_date: datetime | None = None, restaurant_id: str | None = None) -> list[DailyMenuModel]:
        target_restaurant_id = restaurent_id or restaurant_id
        statement = select(DailyMenuModel).where(DailyMenuModel.restaurant_id == _as_str(target_restaurant_id))
        if start_date is not None:
            statement = statement.where(DailyMenuModel.date >= start_date)
        if end_date is not None:
            statement = statement.where(DailyMenuModel.date <= end_date)
        result = await self.session.execute(
            statement.options(selectinload(DailyMenuModel.meal_availabilities).selectinload(MealAvailabilityModel.meal)).order_by(DailyMenuModel.date.asc())
        )
        return list(result.scalars().unique().all())

    async def get_by_restaurent_by_date(self, restaurent_id: str | None = None, date: datetime | None = None, restaurant_id: str | None = None) -> Optional[DailyMenuModel]:
        target_restaurant_id = restaurent_id or restaurant_id
        target_date = date.date() if isinstance(date, datetime) else date
        date_clause = func.date(DailyMenuModel.date) == target_date if target_date is not None else True
        result = await self.session.execute(
            select(DailyMenuModel)
            .options(selectinload(DailyMenuModel.meal_availabilities).selectinload(MealAvailabilityModel.meal))
            .where(DailyMenuModel.restaurant_id == _as_str(target_restaurant_id), date_clause)
        )
        return result.scalar_one_or_none()

    async def get_by_restaurant_and_date(self, restaurant_id: str, date: datetime) -> Optional[DailyMenuModel]:
        return await self.get_by_restaurent_by_date(restaurant_id=restaurant_id, date=date)

    async def update(self, daily_menu) -> str:
        model = daily_menu if isinstance(daily_menu, DailyMenuModel) else await self.get_by_id(getattr(daily_menu, "id"))
        if not model:
            return ""
        if model is not daily_menu:
            _copy_fields(model, daily_menu, ["restaurant_id", "date", "is_available", "created_by", "stored_available_quantity"])
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id

    async def delete(self, daily_menu_id: str) -> str:
        await self.session.execute(delete(DailyMenuModel).where(DailyMenuModel.id == _as_str(daily_menu_id)))
        await self.session.commit()
        return _as_str(daily_menu_id)

    async def mark_as_available(self, daily_menu_id: str) -> str:
        model = await self.get_by_id(daily_menu_id)
        if model is None:
            return ""
        model.is_available = True
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id

    async def mark_as_unavailable(self, daily_menu_id: str) -> str:
        model = await self.get_by_id(daily_menu_id)
        if model is None:
            return ""
        model.is_available = False
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id


class MealAvailabilityRepository(_RepositoryBase):
    async def create(self, meal_availability) -> str:
        model = meal_availability if isinstance(meal_availability, MealAvailabilityModel) else MealAvailabilityModel()
        if model is not meal_availability:
            _copy_fields(model, meal_availability, ["id", "daily_menu_id", "meal_id", "quantity_available", "quantity_reserved"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def get_by_id(self, meal_availability_id: str) -> Optional[MealAvailabilityModel]:
        result = await self.session.execute(select(MealAvailabilityModel).options(selectinload(MealAvailabilityModel.meal)).where(MealAvailabilityModel.id == _as_str(meal_availability_id)))
        return result.scalar_one_or_none()

    async def get_by_daily_menu_meal(self, daily_menu_id: str, meal_id: str) -> Optional[MealAvailabilityModel]:
        result = await self.session.execute(
            select(MealAvailabilityModel)
            .options(selectinload(MealAvailabilityModel.meal))
            .where(MealAvailabilityModel.daily_menu_id == _as_str(daily_menu_id), MealAvailabilityModel.meal_id == _as_str(meal_id))
        )
        return result.scalar_one_or_none()

    async def get_by_daily_menu(self, daily_menu_id: str) -> list[MealAvailabilityModel]:
        result = await self.session.execute(select(MealAvailabilityModel).options(selectinload(MealAvailabilityModel.meal)).where(MealAvailabilityModel.daily_menu_id == _as_str(daily_menu_id)))
        return list(result.scalars().all())

    async def reserve_quantity(self, meal_availability_id: str, quantity: int) -> str:
        model = await self.get_by_id(meal_availability_id)
        if model is None:
            return ""
        model.quantity_reserved += quantity
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id

    async def release_quantity(self, meal_availability_id: str, quantity: int) -> str:
        model = await self.get_by_id(meal_availability_id)
        if model is None:
            return ""
        model.quantity_reserved = max(0, model.quantity_reserved - quantity)
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id

    async def get_available_quantity(self, meal_availability_id: str) -> int:
        model = await self.get_by_id(meal_availability_id)
        return model.remaining_quantity if model else 0

    async def update(self, meal_availability) -> str:
        model = meal_availability if isinstance(meal_availability, MealAvailabilityModel) else await self.get_by_id(getattr(meal_availability, "id"))
        if not model:
            return ""
        if model is not meal_availability:
            _copy_fields(model, meal_availability, ["daily_menu_id", "meal_id", "quantity_available", "quantity_reserved"])
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id


class TimeSlotAvailabilityRepository(_RepositoryBase):
    async def create(self, time_slot_availability) -> str:
        model = time_slot_availability if isinstance(time_slot_availability, TimeSlotAvailabilityModel) else TimeSlotAvailabilityModel()
        if model is not time_slot_availability:
            _copy_fields(model, time_slot_availability, ["id", "time_slot_id", "date", "quantity_available", "quantity_reserved"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def get_by_id(self, time_slot_availability_id: str) -> Optional[TimeSlotAvailabilityModel]:
        result = await self.session.execute(select(TimeSlotAvailabilityModel).options(selectinload(TimeSlotAvailabilityModel.time_slot)).where(TimeSlotAvailabilityModel.id == _as_str(time_slot_availability_id)))
        return result.scalar_one_or_none()

    async def get_by_slot_date(self, time_slot_id: str, date: datetime) -> Optional[TimeSlotAvailabilityModel]:
        target_date = date.date() if isinstance(date, datetime) else date
        date_clause = func.date(TimeSlotAvailabilityModel.date) == target_date if target_date is not None else True
        result = await self.session.execute(
            select(TimeSlotAvailabilityModel)
            .options(selectinload(TimeSlotAvailabilityModel.time_slot))
            .where(TimeSlotAvailabilityModel.time_slot_id == _as_str(time_slot_id), date_clause)
        )
        return result.scalar_one_or_none()

    async def get_by_slot(self, time_slot_id: str) -> list[TimeSlotAvailabilityModel]:
        result = await self.session.execute(select(TimeSlotAvailabilityModel).options(selectinload(TimeSlotAvailabilityModel.time_slot)).where(TimeSlotAvailabilityModel.time_slot_id == _as_str(time_slot_id)))
        return list(result.scalars().all())

    async def reserve_slot(self, time_slot_availability_id: str, quantity: int) -> str:
        model = await self.get_by_id(time_slot_availability_id)
        if model is None:
            return ""
        model.quantity_reserved += quantity
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id

    async def release_slot(self, time_slot_availability_id: str, quantity: int) -> str:
        model = await self.get_by_id(time_slot_availability_id)
        if model is None:
            return ""
        model.quantity_reserved = max(0, model.quantity_reserved - quantity)
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id

    async def get_available_slots(self, time_slot_id: str | None = None, date: datetime | None = None, restaurent_id: str | None = None) -> list[TimeSlotAvailabilityModel]:
        statement = select(TimeSlotAvailabilityModel).options(selectinload(TimeSlotAvailabilityModel.time_slot))
        if time_slot_id is not None:
            statement = statement.where(TimeSlotAvailabilityModel.time_slot_id == _as_str(time_slot_id))
        if date is not None:
            target_date = date.date() if isinstance(date, datetime) else date
            statement = statement.where(func.date(TimeSlotAvailabilityModel.date) == target_date)
        if restaurent_id is not None:
            statement = statement.join(TimeSlotModel).where(TimeSlotModel.restaurant_id == _as_str(restaurent_id))
        result = await self.session.execute(statement.order_by(TimeSlotAvailabilityModel.date.asc()))
        return [slot for slot in result.scalars().all() if slot.quantity_available > slot.quantity_reserved]

    async def has_capacity(self, restaurant_id: str, time_slot_id: str, date: datetime) -> bool:
        slots = await self.get_available_slots(time_slot_id=time_slot_id, date=date, restaurent_id=restaurant_id)
        if not slots:
            result = await self.session.execute(select(TimeSlotModel).where(TimeSlotModel.id == _as_str(time_slot_id), TimeSlotModel.restaurant_id == _as_str(restaurant_id)))
            slot = result.scalar_one_or_none()
            return bool(slot and slot.capacity > 0)
        return any(slot.quantity_available > slot.quantity_reserved for slot in slots)

    async def update(self, time_slot_availability) -> str:
        model = time_slot_availability if isinstance(time_slot_availability, TimeSlotAvailabilityModel) else await self.get_by_id(getattr(time_slot_availability, "id"))
        if not model:
            return ""
        if model is not time_slot_availability:
            _copy_fields(model, time_slot_availability, ["time_slot_id", "date", "quantity_available", "quantity_reserved"])
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id


class ReservationItemRepository(_RepositoryBase):
    async def create(self, reservation_item) -> str:
        model = reservation_item if isinstance(reservation_item, ReservationItemModel) else ReservationItemModel()
        if model is not reservation_item:
            _copy_fields(model, reservation_item, ["id", "reservation_id", "meal_id", "quantity", "unit_price", "subtotal"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def get_by_id(self, reservation_item_id: str) -> Optional[ReservationItemModel]:
        result = await self.session.execute(select(ReservationItemModel).options(selectinload(ReservationItemModel.meal)).where(ReservationItemModel.id == _as_str(reservation_item_id)))
        return result.scalar_one_or_none()

    async def get_by_reservation(self, reservation_id: str) -> list[ReservationItemModel]:
        result = await self.session.execute(select(ReservationItemModel).options(selectinload(ReservationItemModel.meal)).where(ReservationItemModel.reservation_id == _as_str(reservation_id)))
        return list(result.scalars().all())

    async def update(self, reservation_item) -> str:
        model = reservation_item if isinstance(reservation_item, ReservationItemModel) else await self.get_by_id(getattr(reservation_item, "id"))
        if not model:
            return ""
        if model is not reservation_item:
            _copy_fields(model, reservation_item, ["reservation_id", "meal_id", "quantity", "unit_price", "subtotal"])
        await self.session.commit()
        return model.id

    async def delete(self, reservation_item_id: str) -> str:
        await self.session.execute(delete(ReservationItemModel).where(ReservationItemModel.id == _as_str(reservation_item_id)))
        await self.session.commit()
        return _as_str(reservation_item_id)


class ReservationModificationRepository(_RepositoryBase):
    async def create(self, reservation_modification) -> str:
        model = reservation_modification if isinstance(reservation_modification, ReservationModificationModel) else ReservationModificationModel()
        if model is not reservation_modification:
            _copy_fields(model, reservation_modification, ["id", "reservation_id", "modification_type", "old_value", "new_value", "price_adjustment"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def get_by_reservation(self, reservation_id: str) -> list[ReservationModificationModel]:
        result = await self.session.execute(select(ReservationModificationModel).where(ReservationModificationModel.reservation_id == _as_str(reservation_id)))
        return list(result.scalars().all())

    async def get_by_type(self, reservation_id: str, modification_type: ReservationModificationType) -> list[ReservationModificationModel]:
        result = await self.session.execute(select(ReservationModificationModel).where(ReservationModificationModel.reservation_id == _as_str(reservation_id), ReservationModificationModel.modification_type == modification_type))
        return list(result.scalars().all())


class NotificationRepository(_RepositoryBase):
    async def create(self, notification) -> str:
        model = notification if isinstance(notification, NotificationModel) else NotificationModel()
        if model is not notification:
            _copy_fields(model, notification, ["id", "student_id", "reservation_id", "notification_type", "title", "message", "status", "sent_at", "read_at"])
        if model.sent_at is None:
            model.sent_at = _utcnow()
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def save(self, notification) -> NotificationModel:
        model = notification if isinstance(notification, NotificationModel) else NotificationModel()
        if model is not notification:
            _copy_fields(model, notification, ["id", "student_id", "reservation_id", "notification_type", "title", "message", "status", "sent_at", "read_at"])
        if model.sent_at is None:
            model.sent_at = _utcnow()
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_by_id(self, notification_id: str) -> Optional[NotificationModel]:
        result = await self.session.execute(select(NotificationModel).where(NotificationModel.id == _as_str(notification_id)))
        return result.scalar_one_or_none()

    async def get_by_reservation(self, reservation_id: str) -> list[NotificationModel]:
        result = await self.session.execute(select(NotificationModel).where(NotificationModel.reservation_id == _as_str(reservation_id)).order_by(NotificationModel.created_at.desc()))
        return list(result.scalars().all())

    async def get_pending_notifications(self) -> list[NotificationModel]:
        result = await self.session.execute(select(NotificationModel).where(NotificationModel.status == NotificationStatus.PENDING))
        return list(result.scalars().all())

    async def get_by_student(self, student_id: str) -> list[NotificationModel]:
        result = await self.session.execute(select(NotificationModel).where(NotificationModel.student_id == _as_str(student_id)).order_by(NotificationModel.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_type(self, notification_type: NotificationType) -> list[NotificationModel]:
        result = await self.session.execute(select(NotificationModel).where(NotificationModel.notification_type == notification_type))
        return list(result.scalars().all())

    async def update_status(self, notification_id: str, status: NotificationStatus) -> NotificationModel:
        model = await self.get_by_id(notification_id)
        if model is None:
            return None
        model.status = status
        if model.sent_at is None:
            model.sent_at = _utcnow()
        if status == NotificationStatus.READ:
            model.read_at = _utcnow()
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def mark_sent(self, notification_id: str) -> str:
        model = await self.update_status(notification_id, NotificationStatus.SENT)
        return model.id if model else ""

    async def mark_read(self, notification_id: str) -> str:
        model = await self.update_status(notification_id, NotificationStatus.READ)
        return model.id if model else ""

    async def update(self, notification) -> str:
        model = notification if isinstance(notification, NotificationModel) else await self.get_by_id(getattr(notification, "id"))
        if not model:
            return ""
        if model is not notification:
            _copy_fields(model, notification, ["student_id", "reservation_id", "notification_type", "title", "message", "status", "sent_at", "read_at"])
        await self.session.commit()
        return model.id

    async def get_by_student_id(self, student_id: str, limit: int = 50, offset: int = 0, status: NotificationStatus | None = None) -> list[NotificationModel]:
        statement = select(NotificationModel).where(NotificationModel.student_id == _as_str(student_id))
        if status is not None:
            statement = statement.where(NotificationModel.status == status)
        result = await self.session.execute(statement.order_by(NotificationModel.created_at.desc()).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def count_by_student_id(self, student_id: str, status: NotificationStatus | None = None) -> int:
        statement = select(func.count(NotificationModel.id)).where(NotificationModel.student_id == _as_str(student_id))
        if status is not None:
            statement = statement.where(NotificationModel.status == status)
        result = await self.session.execute(statement)
        return int(result.scalar_one() or 0)


class PaymentTransactionRepository(_RepositoryBase):
    async def save(self, transaction) -> PaymentTransactionModel:
        model = transaction if isinstance(transaction, PaymentTransactionModel) else PaymentTransactionModel()
        if model is not transaction:
            _copy_fields(model, transaction, ["id", "student_id", "reservation_id", "amount", "transaction_type", "status", "payment_method", "reference_id"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_by_id(self, transaction_id: str) -> Optional[PaymentTransactionModel]:
        result = await self.session.execute(select(PaymentTransactionModel).where(PaymentTransactionModel.id == _as_str(transaction_id)))
        return result.scalar_one_or_none()

    async def get_by_reservation_id(self, reservation_id: str) -> list[PaymentTransactionModel]:
        result = await self.session.execute(select(PaymentTransactionModel).where(PaymentTransactionModel.reservation_id == _as_str(reservation_id)).order_by(PaymentTransactionModel.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_student_id(self, student_id: str) -> list[PaymentTransactionModel]:
        result = await self.session.execute(select(PaymentTransactionModel).where(PaymentTransactionModel.student_id == _as_str(student_id)).order_by(PaymentTransactionModel.created_at.desc()))
        return list(result.scalars().all())


class ReservationRepository(_RepositoryBase):
    async def create(self, reservation) -> str:
        model = reservation if isinstance(reservation, ReservationModel) else ReservationModel()
        if model is not reservation:
            _copy_fields(model, reservation, ["id", "student_id", "restaurant_id", "date", "time_slot_id", "status", "total_price", "confirmation_number", "qr_code_path", "created_at", "updated_at", "canceled_at", "completed_at"])
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.id

    async def _load(self, reservation_id: str) -> Optional[ReservationModel]:
        result = await self.session.execute(
            select(ReservationModel)
            .options(
                selectinload(ReservationModel.restaurant),
                selectinload(ReservationModel.time_slot),
                selectinload(ReservationModel.items).selectinload(ReservationItemModel.meal),
                selectinload(ReservationModel.notifications),
                selectinload(ReservationModel.transactions),
                selectinload(ReservationModel.modifications),
            )
            .where(ReservationModel.id == _as_str(reservation_id))
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, reservation_id: str) -> Optional[ReservationModel]:
        return await self._load(reservation_id)

    async def get_by_confirmation_number(self, confirmation_number: str) -> Optional[ReservationModel]:
        result = await self.session.execute(
            select(ReservationModel)
            .options(selectinload(ReservationModel.restaurant), selectinload(ReservationModel.time_slot), selectinload(ReservationModel.items).selectinload(ReservationItemModel.meal))
            .where(ReservationModel.confirmation_number == confirmation_number)
        )
        return result.scalar_one_or_none()

    async def get_by_student_id(self, student_id: str) -> list[ReservationModel]:
        result = await self.session.execute(
            select(ReservationModel)
            .options(selectinload(ReservationModel.restaurant), selectinload(ReservationModel.time_slot), selectinload(ReservationModel.items).selectinload(ReservationItemModel.meal))
            .where(ReservationModel.student_id == _as_str(student_id))
            .order_by(ReservationModel.date.desc())
        )
        return list(result.scalars().all())

    async def get_upcoming_reservations(self, student_id: str) -> list[ReservationModel]:
        today = _utcnow().date()
        active_statuses = [ReservationStatus.CONFIRMED]
        if hasattr(ReservationStatus, "PENDING"):
            active_statuses.append(ReservationStatus.PENDING)
        result = await self.session.execute(
            select(ReservationModel)
            .options(selectinload(ReservationModel.restaurant), selectinload(ReservationModel.time_slot), selectinload(ReservationModel.items).selectinload(ReservationItemModel.meal))
            .where(ReservationModel.student_id == _as_str(student_id), func.date(ReservationModel.date) >= today, ReservationModel.status.in_(active_statuses))
            .order_by(ReservationModel.date.asc())
        )
        return list(result.scalars().all())

    async def get_reservation_history(self, student_id: str) -> list[ReservationModel]:
        result = await self.session.execute(
            select(ReservationModel)
            .options(selectinload(ReservationModel.restaurant), selectinload(ReservationModel.time_slot), selectinload(ReservationModel.items).selectinload(ReservationItemModel.meal))
            .where(ReservationModel.student_id == _as_str(student_id), ReservationModel.date < _utcnow())
            .order_by(ReservationModel.date.desc())
        )
        return list(result.scalars().all())

    async def get_by_restaurent(self, restaurent_id: str) -> list[ReservationModel]:
        result = await self.session.execute(
            select(ReservationModel)
            .options(selectinload(ReservationModel.restaurant), selectinload(ReservationModel.time_slot), selectinload(ReservationModel.items).selectinload(ReservationItemModel.meal))
            .where(ReservationModel.restaurant_id == _as_str(restaurent_id))
            .order_by(ReservationModel.date.desc())
        )
        return list(result.scalars().all())

    async def get_by_restaurent_slot(self, restaurent_id: str, date: datetime, time_slot: str) -> list[ReservationModel]:
        result = await self.session.execute(
            select(ReservationModel)
            .options(selectinload(ReservationModel.restaurant), selectinload(ReservationModel.time_slot), selectinload(ReservationModel.items).selectinload(ReservationItemModel.meal))
            .where(ReservationModel.restaurant_id == _as_str(restaurent_id), func.date(ReservationModel.date) == date.date() if isinstance(date, datetime) else date, ReservationModel.time_slot_id == _as_str(time_slot))
        )
        return list(result.scalars().all())

    async def update(self, reservation) -> str:
        model = reservation if isinstance(reservation, ReservationModel) else await self._load(getattr(reservation, "id"))
        if not model:
            return ""
        if model is not reservation:
            _copy_fields(model, reservation, ["student_id", "restaurant_id", "date", "time_slot_id", "status", "total_price", "confirmation_number", "qr_code_path", "canceled_at", "completed_at", "reminder_24h_sent_at", "reminder_1h_sent_at"])
        model.updated_at = _utcnow()
        await self.session.commit()
        return model.id

    async def update_status(self, reservation_id: str, status: ReservationStatus) -> str:
        model = await self._load(reservation_id)
        if not model:
            return ""
        model.status = status
        model.updated_at = _utcnow()
        if status == ReservationStatus.CANCELLED:
            model.canceled_at = _utcnow()
        if status == ReservationStatus.COMPLETED:
            model.completed_at = _utcnow()
        await self.session.commit()
        return model.id

    async def cancel(self, reservation_id: str) -> str:
        return await self.update_status(reservation_id, ReservationStatus.CANCELLED)

    async def mark_completed(self, reservation_id: str) -> str:
        return await self.update_status(reservation_id, ReservationStatus.COMPLETED)

    async def check_double_booking(self, student_id: str, date: datetime, time_slot: str) -> bool:
        active_statuses = [ReservationStatus.CONFIRMED]
        if hasattr(ReservationStatus, "PENDING"):
            active_statuses.append(ReservationStatus.PENDING)
        target_date = date.date() if isinstance(date, datetime) else date
        date_clause = func.date(ReservationModel.date) == target_date if target_date is not None else True
        result = await self.session.execute(
            select(func.count(ReservationModel.id)).where(
                ReservationModel.student_id == _as_str(student_id),
                date_clause,
                ReservationModel.time_slot_id == _as_str(time_slot),
                ReservationModel.status.in_(active_statuses),
            )
        )
        return int(result.scalar_one() or 0) > 0

    async def get_pending_reminders(self, target_date: datetime, limit: int = 100) -> list[ReservationModel]:
        target_day = target_date.date() if isinstance(target_date, datetime) else target_date
        result = await self.session.execute(
            select(ReservationModel)
            .options(selectinload(ReservationModel.restaurant), selectinload(ReservationModel.time_slot), selectinload(ReservationModel.items).selectinload(ReservationItemModel.meal))
            .where(ReservationModel.status == ReservationStatus.CONFIRMED, func.date(ReservationModel.date) == target_day)
            .order_by(ReservationModel.date.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_reminder_sent(self, reservation_id: str, reminder_type: str = "24h") -> str:
        model = await self._load(reservation_id)
        if not model:
            return ""
        now = _utcnow()
        if reminder_type == "1h":
            model.reminder_1h_sent_at = now
        else:
            model.reminder_24h_sent_at = now
        await self.session.commit()
        return model.id


__all__ = [
    "RestaurantRepository",
    "TimeSlotRepository",
    "MealRepository",
    "DailyMenuRepository",
    "MealAvailabilityRepository",
    "TimeSlotAvailabilityRepository",
    "ReservationItemRepository",
    "ReservationModificationRepository",
    "NotificationRepository",
    "PaymentTransactionRepository",
    "ReservationRepository",
]
