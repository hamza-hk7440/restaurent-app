from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from reservation.domain.value_objects.notification_status import NotificationStatus
from reservation.domain.value_objects.notification_type import NotificationType
from reservation.domain.value_objects.transaction_type import TransactionType
from reservation.domain.value_objects.transaction_status import TransactionStatus
class PaymentTransactionResponseDTO(BaseModel):
    transaction_id: UUID
    reservation_id: UUID
    student_id: UUID
    amount: Annotated[float, Field(description="The amount of the payment transaction.")]
    transaction_type: Annotated[TransactionType, Field(description="The type of the payment transaction.")]
    transaction_status: Annotated[TransactionStatus, Field(description="The status of the payment transaction .")]
    payment_method: Annotated[str, Field(description="The payment method used for the transaction.")]
    reference_id: Annotated[str, Field(description="The reference ID for the payment transaction.")]
    created_at: Annotated[datetime, Field(description="The timestamp when the payment transaction was created.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174007",
                "reservation_id": "123e4567-e89b-12d3-a456-426614174005",
                "student_id": "123e4567-e89b-12d3-a456-426614174006",
                "amount": 31.98,
                "transaction_type": "payment",
                "transaction_status": "completed",
                "payment_method": "credit_card",
                "reference_id": "REF1234567890",
                "created_at": "2023-10-15T18:30:00Z"
            }
        }
    )
    @classmethod
    def from_entity(cls, payment_transaction) -> 'PaymentTransactionResponseDTO':
        return cls(
            transaction_id=payment_transaction.transaction_id,
            reservation_id=payment_transaction.reservation_id,
            student_id=payment_transaction.student_id,
            amount=payment_transaction.amount,
            transaction_type=payment_transaction.transaction_type,
            transaction_status=payment_transaction.transaction_status,
            payment_method=payment_transaction.payment_method,
            reference_id=payment_transaction.reference_id,
            created_at=payment_transaction.created_at
        )
class NotificationResponseDTO(BaseModel):
    id: UUID
    student_id: UUID
    reservation_id: UUID
    notification_type: Annotated[NotificationType, Field(description="The type of the notification.")]
    title: Annotated[str, Field(description="The title of the notification.")]
    message: Annotated[str, Field(description="The message content of the notification.")]
    status:Annotated[NotificationStatus, Field(description="The status of the notification.")]
    sent_at: Annotated[datetime, Field(description="The timestamp when the notification was sent.")]
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174008",
                "student_id": "123e4567-e89b-12d3-a456-426614174006",
                "reservation_id": "123e4567-e89b-12d3-a456-426614174005",
                "notification_type": "reminder",
                "title": "Reservation Confirmation",
                "message": "Your reservation has been confirmed.",
                "status": "sent",
                "sent_at": "2023-10-15T18:30:00Z"
            }
        }
    )
    @classmethod
    def from_entity(cls, notification) -> 'NotificationResponseDTO':
        return cls(
            id=notification.id,
            student_id=notification.student_id,
            reservation_id=notification.reservation_id,
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            status=notification.status,
            sent_at=notification.sent_at
        )
