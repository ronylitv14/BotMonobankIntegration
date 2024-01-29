import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from aiogram.enums import ChatType


class ChatDataRequest(BaseModel):
    chat_id: int
    task_id: int
    group_name: str
    invite_link: str
    participants_count: int
    client_id: int
    executor_id: int
    chat_admin: str
    supergroup_id: Optional[int] = None


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: int
    chat_id: int
    supergroup_id: Optional[int] = None
    task_id: int
    executor_id: int
    client_id: int
    group_name: str
    chat_type: ChatType
    chat_admin: str
    active: bool = True
    is_payed: bool = False
    date_created: datetime.datetime
    payment_date: Optional[datetime.datetime] = None
    participants_count: Optional[int] = None
    invite_link: Optional[str] = None
    in_use: bool


class UpdateChatStatusRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    chat_type: ChatType
    supergroup_id: int
    db_chat_id: int


class UpdateGroupTitleRequest(BaseModel):
    db_chat_id: int
    group_name: str


class UpdateChatField(BaseModel):
    # db_chat_id: int
    active: Optional[bool] = None
    group_name: Optional[str] = None
    participants_count: Optional[int] = None
    in_use: Optional[bool] = None

