from typing import Annotated,List,Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from reservation.domain.value_objects.reservation_modification_type import ReservationModificationType

class ReservationItemCreateDTO(BaseModel):
    meal_id: UUID
    quantity: Annotated[int, Field(description="The quantity of the meal to be reserved.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "meal_id": "123e4567-e89b-12d3-a456-426614174002",
                "quantity": 2
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation_item) -> 'ReservationItemCreateDTO':
        return cls(
            meal_id=reservation_item.meal_id,
            quantity=reservation_item.quantity
        )
class CreateReservationRequestDTO(BaseModel):
    restaurent_id: UUID
    date: Annotated[datetime, Field(description="The date of the reservation.")]
    time_slot_id: UUID
    items: Annotated[list[ReservationItemCreateDTO], Field(description="The list of reservation items.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "restaurent_id": "123e4567-e89b-12d3-a456-426614174000",
                "date": "2023-10-01T12:00:00",
                "time_slot_id": "123e4567-e89b-12d3-a456-426614174001",
                "items": [
                    {
                        "meal_id": "123e4567-e89b-12d3-a456-426614174002",
                        "quantity": 2
                    }
                ]
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation) -> 'CreateReservationRequestDTO':
        return cls(
            restaurent_id=reservation.restaurent_id,
            date=reservation.date,
            time_slot_id=reservation.time_slot_id,
            items=[ReservationItemCreateDTO.from_entity(item) for item in reservation.items]
        )
class ModifyReservationRequestDTO(BaseModel):
    modification_type: Annotated[ReservationModificationType, Field(description="The type of modification to be made to the reservation.")]
    new_time_slot_id: UUID | None = Field(default=None, description="The new time slot ID for the reservation, if applicable.")
    new_items: Annotated[list[ReservationItemCreateDTO] | None, Field(description="The new list of reservation items, if applicable.")] = None
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "modification_type": "change_time_slot",
                "new_time_slot_id": "123e4567-e89b-12d3-a456-426614174001",
                "new_items": [
                    {
                        "meal_id": "123e4567-e89b-12d3-a456-426614174002",
                        "quantity": 2
                    }
                ]
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation_modification) -> 'ModifyReservationRequestDTO':
        return cls(
            modification_type=reservation_modification.modification_type,
            new_time_slot_id=reservation_modification.new_time_slot_id,
            new_items=[ReservationItemCreateDTO.from_entity(item) for item in reservation_modification.new_items] if reservation_modification.new_items else None
        )
class CancelReservationRequestDTO(BaseModel):
    reason:Annotated[str, Field(description="The reason for canceling the reservation.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "reason": "Change of plans"
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation_cancellation) -> 'CancelReservationRequestDTO':
        return cls(
            reason=reservation_cancellation.reason
        )
@dataclass(frozen=True)
class CreateReservationLockCommand:
    student_id: UUID
    restaurent_id: UUID
    date: datetime
    time_slot_id: UUID
    items:List[ReservationItemCreateDTO]
class ReservationLockResponseDTO(BaseModel):
    lock_id: UUID
    student_id: UUID
    restaurent_id: UUID
    time_slot_id: UUID
    expires_at:datetime
    is_active:bool

    model_config= ConfigDict(
        from_attributes=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "lock_id": "123e4567-e89b-12d3-a456-426614174003",
                "student_id": "123e4567-e89b-12d3-a456-426614174004",
                "restaurent_id": "123e4567-e89b-12d3-a456-426614174000",
                "time_slot_id": "123e4567-e89b-12d3-a456-426614174001",
                "expires_at": "2023-10-01T12:30:00",
                "is_active": True
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation_lock) -> 'ReservationLockResponseDTO':
        return cls(
            lock_id=reservation_lock.lock_id,
            student_id=reservation_lock.student_id,
            restaurent_id=reservation_lock.restaurent_id,
            time_slot_id=reservation_lock.time_slot_id,
            expires_at=reservation_lock.expires_at,
            is_active=reservation_lock.is_active
        )
@dataclass(frozen=True)
class CancelReservationCommand:
    reservation_id: UUID
    student_id: UUID
    cancellation_reason: str
class ValidateQrCodeCommand:
    reservation_id: UUID
    qr_code_data: str
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "reservation_id": "123e4567-e89b-12d3-a456-426614174005",
                "qr_code_data": "QR_CODE_DATA_STRING"
            }
        }
    )
class ValidateQrCodeResponseDTO(BaseModel):
    is_valid: bool
    reservation_id: UUID
    student_id: UUID
    status: str
    message: str
    validated_at:datetime
    model_config=ConfigDict(extra="forbid")
class MarkReservationCompletedCommand(BaseModel):
    reservation_id:UUID
    student_id:Optional[UUID]
    model_config=ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "reservation_id": "123e4567-e89b-12d3-a456-426614174005",
                "student_id": "123e4567-e89b-12d3-a456-426614174006",
            }
        },
    )
class MarkReservationNoShowCommand(BaseModel):
    reservation_id:UUID
    restaurent_id:Optional[UUID]
    reason:Optional[str]
    model_config=ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "reservation_id": "123e4567-e89b-12d3-a456-426614174005",
                "restaurent_id": "123e4567-e89b-12d3-a456-426614174000",
                "reason": "Customer did not show up."
            }
        },
    )