from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.value_objects.reservation_modification_type import ReservationModificationType
class ReservationItemResponseDTO(BaseModel):
    id: UUID
    meal_id: UUID
    meal_name: Annotated[str, Field(description="The name of the meal reserved.")]
    quantity: Annotated[int, Field(description="The quantity of the meal reserved.")]
    unit_price: Annotated[float, Field(description="The unit price of the meal reserved.")]
    subtotal: Annotated[float, Field(description="The subtotal price for the reserved meal (unit price * quantity).")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174004",
                "meal_id": "123e4567-e89b-12d3-a456-426614174002",
                "meal_name": "Grilled Salmon",
                "quantity": 2,
                "unit_price": 15.99,
                "subtotal": 31.98
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation_item) -> 'ReservationItemResponseDTO':
        return cls(
            id=reservation_item.id,
            meal_id=reservation_item.meal_id,
            meal_name=reservation_item.meal_name,
            quantity=reservation_item.quantity,
            unit_price=reservation_item.unit_price,
            subtotal=reservation_item.subtotal
        )
class ReservationResponseDTO(BaseModel):
    id: UUID
    restaurent_id: UUID
    student_id: UUID
    restaurent_name: Annotated[str, Field(description="The name of the restaurant where the reservation was made.")]
    date: Annotated[datetime, Field(description="The date of the reservation.")]
    time_slot_id: UUID
    confirmation_code: Annotated[str, Field(description="The confirmation code for the reservation.")]
    qr_code_path: Annotated[str, Field(description="The path to the QR code for the reservation.")]
    items: Annotated[list[ReservationItemResponseDTO], Field(description="The list of reservation items.")]
    created_at: Annotated[datetime, Field(description="The timestamp when the reservation was created.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174005",
                "restaurent_id": "123e4567-e89b-12d3-a456-426614174000",
                "student_id": "123e4567-e89b-12d3-a456-426614174006",
                "restaurent_name": "The Great Restaurant",
                "date": "2023-10-15T18:00:00Z",
                "time_slot_id": "123e4567-e89b-12d3-a456-426614174001",
                "confirmation_code": "CONF123456",
                "qr_code_path": "/qr_codes/reservation_123e4567-e89b-12d3-a456-426614174005.png",
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174004",
                        "meal_id": "123e4567-e89b-12d3-a456-426614174002",
                        "meal_name": "Grilled Salmon",
                        "quantity": 2,
                        "unit_price": 15.99,
                        "subtotal": 31.98
                    }
                ],
                "created_at": "2023-10-10T12:00:00Z"
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation) -> 'ReservationResponseDTO':
        return cls(
            id=reservation.id,
            restaurent_id=reservation.restaurent_id,
            student_id=reservation.student_id,
            restaurent_name=reservation.restaurent_name,
            date=reservation.date,
            time_slot_id=reservation.time_slot_id,
            confirmation_code=reservation.confirmation_code,
            qr_code_path=reservation.qr_code_path,
            items=[ReservationItemResponseDTO.from_entity(item) for item in reservation.items],
            created_at=reservation.created_at
        )
class ReservationSummaryDTO(BaseModel):
    id: UUID
    restaurent_name: Annotated[str, Field(description="The name of the restaurant where the reservation was made.")]
    date: Annotated[datetime, Field(description="The date of the reservation.")]
    time_slot_label: Annotated[str, Field(description="The label of the time slot for the reservation.")]
    status: Annotated[ReservationStatus, Field(description="The status of the reservation.")]
    total_price: Annotated[float, Field(description="The total price of the reservation.")]
    items_count: Annotated[int, Field(description="The total number of items in the reservation.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174005",
                "restaurent_name": "The Great Restaurant",
                "date": "2023-10-15T18:00:00Z",
                "time_slot_label": "6:00 PM - 8:00 PM",
                "status": "CONFIRMED",
                "total_price": 31.98,
                "items_count": 2
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation) -> 'ReservationSummaryDTO':
        return cls(
            id=reservation.id,
            restaurent_name=reservation.restaurent_name,
            date=reservation.date,
            time_slot_label=reservation.time_slot_label,
            status=reservation.status,
            total_price=reservation.total_price,
            items_count=reservation.items_count
        )
class ReservationModificationResponseDTO(BaseModel):
    id: UUID
    reservation_id: UUID
    modification_type: Annotated[ReservationModificationType, Field(description="The type of modification made to the reservation.")]
    old_value: Annotated[str | None, Field(description="The old value before the modification, if applicable.")]
    new_value: Annotated[str | None, Field(description="The new value after the modification, if applicable.")]
    price_adjustment: Annotated[float, Field(description="The price adjustment resulting from the modification.")]
    created_at: Annotated[datetime, Field(description="The timestamp when the modification was made.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174007",
                "reservation_id": "123e4567-e89b-12d3-a456-426614174005",
                "modification_type": "change_time_slot",
                "old_value": "6:00 PM - 8:00 PM",
                "new_value": "8:00 PM - 10:00 PM",
                "price_adjustment": 5.0,
                "created_at": "2023-10-10T12:00:00Z"
            }
        }
    )
    @classmethod
    def from_entity(cls, reservation_modification) -> 'ReservationModificationResponseDTO':
        return cls(
            id=reservation_modification.id,
            reservation_id=reservation_modification.reservation_id,
            modification_type=reservation_modification.modification_type,
            old_value=reservation_modification.old_value,
            new_value=reservation_modification.new_value,
            price_adjustment=reservation_modification.price_adjustment,
            created_at=reservation_modification.created_at
        )