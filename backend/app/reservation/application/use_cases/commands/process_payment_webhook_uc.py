from typing import Dict, Tuple
from uuid import UUID

from reservation.domain.entities.reservation_entity import Reservation
from reservation.domain.entities.transaction_entity import Transaction 
from reservation.domain.value_objects.reservation_status import ReservationStatus
from reservation.domain.value_objects.transaction_status import TransactionStatus
from reservation.domain.value_objects.transaction_type import TransactionType
from reservation.domain.interfaces.reservation_repo import IReservationRepository
from reservation.domain.interfaces.payment_transaction_repo import IPaymentTransactionRepository
from reservation.domain.exceptions.domain_exceptions import (
    ReservationNotFoundException,
    InvalidPaymentWebhookException,
)
from reservation.application.dtos.payment_and_notification_dtos import PaymentTransactionResponseDTO,ProcessPaymentWebhookCommand
class ProcessPaymentWebhookUseCase:
    STATUS_MAPPING: Dict[str, Tuple[ReservationStatus, TransactionStatus]] = {
        "SUCCESS": (ReservationStatus.CONFIRMED, TransactionStatus.COMPLETED),
        "COMPLETED": (ReservationStatus.CONFIRMED, TransactionStatus.COMPLETED),
        "FAILED": (ReservationStatus.CANCELLED, TransactionStatus.FAILED),
        "EXPIRED": (ReservationStatus.CANCELLED, TransactionStatus.FAILED),
        "REFUNDED": (ReservationStatus.CANCELLED, TransactionStatus.REFUNDED),
    }

    def __init__(
        self,
        reservation_repository: IReservationRepository,
        payment_transaction_repository: IPaymentTransactionRepository,
    ):
        self._reservation_repo = reservation_repository
        self._payment_transaction_repo = payment_transaction_repository

    async def execute(self, command: ProcessPaymentWebhookCommand) -> PaymentTransactionResponseDTO:
        self._validate_command_payload(command)

        reservation = await self._get_reservation_or_raise(command.reservation_id)
        res_status, tx_status = self._resolve_target_statuses(command.payment_status)

        await self._sync_reservation_status(reservation, res_status)

        transaction_entity = self._build_transaction_entity(
            command=command,
            student_id=reservation.student_id,
            tx_status=tx_status,
        )

        persisted_transaction = await self._payment_transaction_repo.save(transaction_entity)
        return PaymentTransactionResponseDTO.from_entity(persisted_transaction)

    @staticmethod
    def _validate_command_payload(command: ProcessPaymentWebhookCommand) -> None:
        if not command.reservation_id or not command.transaction_id:
            raise InvalidPaymentWebhookException("Webhook command is missing required identifiers.")

    async def _get_reservation_or_raise(self, reservation_id: UUID) -> Reservation:
        reservation = await self._reservation_repo.get_by_id(str(reservation_id))
        if not reservation:
            raise ReservationNotFoundException(f"Reservation with ID '{reservation_id}' not found.")
        return reservation

    @classmethod
    def _resolve_target_statuses(
        cls, payment_status: str
    ) -> Tuple[ReservationStatus, TransactionStatus]:
        normalized = payment_status.upper()
        if normalized not in cls.STATUS_MAPPING:
            raise InvalidPaymentWebhookException(f"Unsupported payment status: '{payment_status}'")
        return cls.STATUS_MAPPING[normalized]

    async def _sync_reservation_status(
        self, reservation: Reservation, target_status: ReservationStatus
    ) -> None:
        current_status_val = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )
        if current_status_val != target_status.value:
            await self._reservation_repo.update_status(reservation.id, target_status)

    @staticmethod
    def _build_transaction_entity(
        command: ProcessPaymentWebhookCommand,
        student_id: UUID,
        tx_status: TransactionStatus,
    ) -> Transaction:
        return Transaction(
            transaction_id=command.transaction_id,
            reservation_id=command.reservation_id,
            student_id=student_id,
            amount=command.amount,
            transaction_type=TransactionType.PAYMENT,
            transaction_status=tx_status,
            payment_method=command.payment_method,
            reference_id=command.reference_id,
        )