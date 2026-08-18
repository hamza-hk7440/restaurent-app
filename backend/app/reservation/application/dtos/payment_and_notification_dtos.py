from typing import Annotated, List,Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
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


class KonnectPaymentInitCommand(BaseModel):
    reservation_id: UUID = Field(description="Reservation to attach the payment to.")
    description: str = Field(default="Reservation payment", description="Gateway payment description.")
    token: str = Field(default="TND", description="Currency token.")
    acceptedPaymentMethods: List[str] = Field(default_factory=lambda: ["wallet", "bank_card", "e-DINAR"])
    lifespan: int = Field(default=10, ge=1, le=1440, description="Payment link lifespan in minutes.")
    checkoutForm: bool = Field(default=True)
    addPaymentFeesToAmount: bool = Field(default=True)
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    theme: str = Field(default="dark")

    model_config = ConfigDict(extra="forbid")


class KonnectPaymentInitResponseDTO(BaseModel):
    pay_url: str
    payment_ref: str
    reservation_id: UUID
    amount: float
    token: str
    status: str

    model_config = ConfigDict(extra="forbid")


class KonnectPaymentDetailsResponseDTO(BaseModel):
    payment_id: str
    status: str
    amount_due: float | None = None
    amount: float | None = None
    token: str | None = None
    link: str | None = None
    webhook: str | None = None
    raw: Dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class ProcessPaymentWebhookCommand(BaseModel):
    provider: str = Field(description="Payment provider name, e.g., 'stripe', 'flouci'.")
    event_type: str = Field(description="Type of webhook event received.")
    reservation_id: UUID = Field(description="Target reservation ID.")
    transaction_id: UUID = Field(description="Unique transaction ID.")
    payment_status: str = Field(description="Raw status string from provider.")
    amount: float = Field(description="Transaction monetary amount.")
    payment_method: str = Field(default="online_gateway", description="Method used for payment.")
    reference_id: str = Field(description="Provider external reference ID.")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Raw webhook event payload.")

    model_config = ConfigDict(extra="forbid")
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
class SendScheduledRemindersCommand(BaseModel):
    target_daate:Optional[datetime] = Field(default=None, description="The target date for sending scheduled reminders. If not provided, defaults to the current date.")
    limit:int=Field(default=100, ge=1, le=1000, description="The maximum number of reminders to send in a single batch. Must be between 1 and 1000.")
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "target_daate": "2023-10-15T18:30:00Z",
                "limit": 100
            }
        }
    )
class SendScheduledRemindersResponseDTO(BaseModel):
    total_processed: int
    successful_sent: int
    failed_sent: int
    notification:List[NotificationResponseDTO]
    model_config = ConfigDict(
        extra="forbid")
class GetStudentNotificationsQuery(BaseModel):
    student_id: UUID = Field(description="The ID of the student for whom to retrieve notifications.")
    limit: int = Field(default=50, ge=1, le=1000, description="The maximum number of notifications to retrieve. Must be between 1 and 1000.")
    offset: int = Field(default=0, ge=0, description="The number of notifications to skip before starting to collect the result set. Must be 0 or greater.")
    status: Optional[NotificationStatus] = Field(default=None, description="Filter notifications by their status. If not provided, all statuses will be included.")
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174006",
                "limit": 50,
                "offset": 0,
                "status": "sent"
            }
        }
    )
class PaginatedNotificationsResponseDTO(BaseModel):
    items: List[NotificationResponseDTO]
    total: int
    limit: int
    offset: int
    model_config = ConfigDict(
        extra="forbid")
class MarkNotificationReadCommand(BaseModel):
    notification_id: UUID = Field(description="UUID of the notification to mark as read.")
    student_id: Optional[UUID] = Field(
        default=None, description="Optional student UUID to enforce notification ownership."
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "notification_id": "123e4567-e89b-12d3-a456-426614174008",
                "student_id": "123e4567-e89b-12d3-a456-426614174006",
            }
        },
    )

