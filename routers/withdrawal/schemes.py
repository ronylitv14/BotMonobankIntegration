import decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, condecimal
from database.models import WithdrawalStatus
from typing import Optional
from datetime import datetime


class WithdrawalRequestModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    user_id: int
    amount: decimal.Decimal
    commission: decimal.Decimal
    status: WithdrawalStatus
    payment_method: str


class UpdateWithdrawalRequestModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    request_id: int
    new_status: WithdrawalStatus
    admin_id: int


class WithdrawalResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
    request_id: int
    user_id: int
    amount: condecimal(max_digits=10, decimal_places=2)
    commission: condecimal(max_digits=10, decimal_places=2)
    request_date: datetime
    status: WithdrawalStatus
    payment_method: str
    payment_details: Optional[str] = None
    processed_date: Optional[datetime] = None
    admin_id: Optional[int] = None
    notes: Optional[str] = None