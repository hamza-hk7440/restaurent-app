from __future__ import annotations

from datetime import datetime, timezone,time
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy import Time as SQLTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from user_management.infrastructure.config.database import Base
from reservation.domain.value_objects.meal_availability import MealAvailability
from reservation.domain.value_objects.meal_category import MealCategory
from reservation.domain.value_objects.notification_status import NotificationStatus
from reservation.domain.value_objects.notification_type import NotificationType
from reservation.domain.value_objects.reservation_modification_type import ReservationModificationType
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.value_objects.restaurent_status import RestaurentStatus
from reservation.domain.value_objects.transaction_status import TransactionStatus
from reservation.domain.value_objects.transaction_type import TransactionType


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RestaurantModel(Base):
    __tablename__ = "restaurants"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    establishment_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    opening_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closing_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[RestaurentStatus] = mapped_column(
        SAEnum(RestaurentStatus, name="restaurant_status", native_enum=False),
        nullable=False,
        default=RestaurentStatus.OPEN,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    time_slots: Mapped[list[TimeSlotModel]] = relationship("TimeSlotModel", back_populates="restaurant", cascade="all, delete-orphan")
    daily_menus: Mapped[list[DailyMenuModel]] = relationship("DailyMenuModel", back_populates="restaurant", cascade="all, delete-orphan")
    reservations: Mapped[list[ReservationModel]] = relationship("ReservationModel", back_populates="restaurant", cascade="all, delete-orphan")

    @property
    def adress(self) -> str:
        return self.address


from datetime import datetime, time
from uuid import uuid4
from sqlalchemy import DateTime, ForeignKey, Integer, Time as SQLTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TimeSlotModel(Base):
    __tablename__ = "time_slots"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    restaurant_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(SQLTime, nullable=False)
    end_time: Mapped[time] = mapped_column(SQLTime, nullable=False)

    # Set default > 0 so it passes the DB check constraint
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # Required for self.availabilities and properties to function
    restaurant: Mapped["RestaurantModel"] = relationship("RestaurantModel", back_populates="time_slots")
    availabilities: Mapped[list["TimeSlotAvailabilityModel"]] = relationship(
        "TimeSlotAvailabilityModel",
        back_populates="time_slot",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    reservations: Mapped[list["ReservationModel"]] = relationship(
        "ReservationModel",
        back_populates="time_slot",
        lazy="selectin",
    )
    @property
    def available_seats(self) -> int:
        if not self.availabilities:
            return self.capacity
        latest = max(self.availabilities, key=lambda item: item.date)
        return max(0, latest.quantity_available - latest.quantity_reserved)

    @property
    def is_full(self) -> bool:
        return self.available_seats <= 0

class DailyMenuModel(Base):
    __tablename__ = "daily_menus"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    restaurant_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    stored_available_quantity: Mapped[int] = mapped_column(
        "available_quantity",
        Integer, nullable=False, default=0
    )
    created_by: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=False), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    restaurant: Mapped["RestaurantModel"] = relationship(
        "RestaurantModel", back_populates="daily_menus"
    )
    meal_availabilities: Mapped[list["MealAvailabilityModel"]] = relationship(
        "MealAvailabilityModel",
        back_populates="daily_menu",
        cascade="all, delete-orphan",
    )
    @property
    def available_quantity(self) -> int:
        """Calculates total available quantity dynamically from meal availabilities."""
        return sum(
            availability.quantity_available or 0
            for availability in self.meal_availabilities
        )

    @available_quantity.setter
    def available_quantity(self, value: int) -> None:
        self.stored_available_quantity = value

    @property
    def restaurent_id(self) -> str:
        return self.restaurant_id

    @property
    def meals(self) -> list["MealModel"]:
        return [
            availability.meal
            for availability in self.meal_availabilities
            if availability.meal is not None
        ]

    @property
    def items(self) -> list["MealModel"]:
        """Returns meals via relationship to avoid querying a non-existent DB column."""
        return self.meals

class MealModel(Base):
    __tablename__ = "meals"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    restaurant_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("restaurants.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    category: Mapped[MealCategory] = mapped_column(
        SAEnum(MealCategory, name="meal_category", native_enum=False),
        nullable=False,
    )
    availability_status: Mapped[MealAvailability] = mapped_column(
        SAEnum(MealAvailability, name="meal_availability", native_enum=False),
        nullable=False,
        default=MealAvailability.AVAILABLE,
    )
    meal_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0)
    popularity_score: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    restaurant: Mapped[RestaurantModel] = relationship("RestaurantModel")
    meal_availabilities: Mapped[list[MealAvailabilityModel]] = relationship("MealAvailabilityModel", back_populates="meal")


class MealAvailabilityModel(Base):
    __tablename__ = "meal_availabilities"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    daily_menu_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("daily_menus.id", ondelete="CASCADE"), index=True, nullable=False)
    meal_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("meals.id", ondelete="CASCADE"), index=True, nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    daily_menu: Mapped[DailyMenuModel] = relationship("DailyMenuModel", back_populates="meal_availabilities")
    meal: Mapped[MealModel] = relationship("MealModel", back_populates="meal_availabilities")

    @property
    def remaining_quantity(self) -> int:
        return max(0, self.quantity_available - self.quantity_reserved)

    @property
    def is_sold_out(self) -> bool:
        return self.remaining_quantity <= 0


class TimeSlotAvailabilityModel(Base):
    __tablename__ = "time_slot_availabilities"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    time_slot_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("time_slots.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    time_slot: Mapped[TimeSlotModel] = relationship("TimeSlotModel", back_populates="availabilities")

    @property
    def remaining_quantity(self) -> int:
        return max(0, self.quantity_available - self.quantity_reserved)

    @property
    def available_seats(self) -> int:
        return self.remaining_quantity

    @property
    def is_full(self) -> bool:
        return self.remaining_quantity <= 0


class ReservationModel(Base):
    __tablename__ = "reservations"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    student_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), index=True, nullable=False)
    restaurant_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("restaurants.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    time_slot_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("time_slots.id", ondelete="RESTRICT"), index=True, nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(
        SAEnum(ReservationStatus, name="reservation_status", native_enum=False),
        nullable=False,
        default=ReservationStatus.CONFIRMED,
    )
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    confirmation_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    qr_code_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    restaurant: Mapped[RestaurantModel] = relationship("RestaurantModel", back_populates="reservations")
    time_slot: Mapped[TimeSlotModel] = relationship("TimeSlotModel", back_populates="reservations")
    items: Mapped[list[ReservationItemModel]] = relationship("ReservationItemModel", back_populates="reservation", cascade="all, delete-orphan")
    modifications: Mapped[list[ReservationModificationModel]] = relationship("ReservationModificationModel", back_populates="reservation", cascade="all, delete-orphan")
    notifications: Mapped[list[NotificationModel]] = relationship("NotificationModel", back_populates="reservation", cascade="all, delete-orphan")
    transactions: Mapped[list[PaymentTransactionModel]] = relationship("PaymentTransactionModel", back_populates="reservation", cascade="all, delete-orphan")

    @property
    def restaurent_id(self) -> str:
        return self.restaurant_id

    @property
    def restaurent_name(self) -> str:
        return self.restaurant.name if self.restaurant else ""

    @property
    def restaurant_name(self) -> str:
        return self.restaurent_name

    @property
    def time_slot_label(self) -> str:
        if not self.time_slot:
            return ""
        return f"{self.time_slot.start_time:%H:%M} - {self.time_slot.end_time:%H:%M}"

    @property
    def confirmation_code(self) -> str:
        return self.confirmation_number

    @property
    def items_count(self) -> int:
        return len(self.items)


class ReservationItemModel(Base):
    __tablename__ = "reservation_items"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    reservation_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey("reservations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    meal_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey("meals.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    subtotal: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # Relationships
    reservation: Mapped["ReservationModel"] = relationship(
        "ReservationModel", back_populates="items"
    )
    meal: Mapped["MealModel"] = relationship("MealModel")

    @property
    def meal_name(self) -> str:
        return self.meal.name if self.meal else ""

class ReservationModificationModel(Base):
    __tablename__ = "reservation_modifications"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    reservation_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("reservations.id", ondelete="CASCADE"), index=True, nullable=False)
    modification_type: Mapped[ReservationModificationType] = mapped_column(
        SAEnum(ReservationModificationType, name="reservation_modification_type", native_enum=False),
        nullable=False,
    )
    old_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price_adjustment: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    reservation: Mapped[ReservationModel] = relationship("ReservationModel", back_populates="modifications")


class NotificationModel(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    student_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), index=True, nullable=False)
    reservation_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("reservations.id", ondelete="CASCADE"), index=True, nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType, name="notification_type", native_enum=False),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        SAEnum(NotificationStatus, name="notification_status", native_enum=False),
        nullable=False,
        default=NotificationStatus.PENDING,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    reservation: Mapped[ReservationModel] = relationship("ReservationModel", back_populates="notifications")


class PaymentTransactionModel(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    student_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), index=True, nullable=False)
    reservation_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), ForeignKey("reservations.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    transaction_type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, name="transaction_type", native_enum=False),
        nullable=False,
    )
    status: Mapped[TransactionStatus] = mapped_column(
        SAEnum(TransactionStatus, name="transaction_status", native_enum=False),
        nullable=False,
        default=TransactionStatus.PENDING,
    )
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    reservation: Mapped[ReservationModel] = relationship("ReservationModel", back_populates="transactions")

    @property
    def transaction_id(self) -> str:
        return self.id

    @property
    def transaction_status(self) -> TransactionStatus:
        return self.status


__all__ = [
    "RestaurantModel",
    "TimeSlotModel",
    "DailyMenuModel",
    "MealModel",
    "MealAvailabilityModel",
    "TimeSlotAvailabilityModel",
    "ReservationModel",
    "ReservationItemModel",
    "ReservationModificationModel",
    "NotificationModel",
    "PaymentTransactionModel",
]
