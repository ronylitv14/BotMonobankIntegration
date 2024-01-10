import decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, condecimal
from database.models import TransactionType, TransactionStatus
from datetime import datetime
from typing import Optional, Literal


class SuccessPayment(BaseModel):
    status: bool = False


class TransactionDataRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    invoice_id: str
    amount: decimal.Decimal
    transaction_type: TransactionType
    transaction_status: TransactionStatus
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    task_id: Optional[int] = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    transaction_id: int
    invoice_id: str
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    task_id: Optional[int] = None
    amount: condecimal(max_digits=10, decimal_places=2)
    commission: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    transaction_type: TransactionType
    transaction_status: TransactionStatus
    transaction_date: Optional[datetime] = None


class UpdateTransactionStatusRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    invoice_id: str
    new_status: TransactionStatus


class CreateTransfer(BaseModel):
    receiver_id: int
    sender_id: int
    task_id: int
    amount: decimal.Decimal


class CheckSuccessfulPaymentRequest(BaseModel):
    task_id: int
    receiver_id: int
    sender_id: int


class AcceptDoneOfferRequest(BaseModel):
    transaction_id: int
    task_id: int
    receiver_id: int
    amount: decimal.Decimal
