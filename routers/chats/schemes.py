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
    date_created: datetime.datetime
    participants_count: Optional[int] = None
    invite_link: Optional[str] = None


class ChatObjectRequest(BaseModel):
    chat_id: Optional[int] = None
    db_chat_id: Optional[int] = None


class UpdateChatStatusRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    chat_type: ChatType
    supergroup_id: int
    db_chat_id: int


class UpdateGroupTitleRequest(BaseModel):
    db_chat_id: int
    group_name: str
