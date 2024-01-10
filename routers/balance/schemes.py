import decimal
from typing import List

from pydantic import BaseModel, ConfigDict
from database.crud import BalanceAction


class UpdateUserCardsRequest(BaseModel):
    user_id: int
    card: str


class BalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_cards: List[str]
    balance_money: decimal.Decimal
    user_id: int


class NewBalanceRequest(BaseModel):
    user_id: int
    new_amount: decimal.Decimal


class UpdateBalanceRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    user_id: int
    amount: decimal.Decimal
    action: BalanceAction
