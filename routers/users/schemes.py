from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, StrictInt
from database.models import User, UserStatus

from typing_extensions import Annotated


class UserResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    telegram_id: int
    telegram_username: str
    username: str
    chat_id: int
    user_status: UserStatus
    is_banned: bool
    warning_count: int
    salt: str
    hashed_password: str
    phone: str
    email: Optional[str] = None


class UserCreateRequest(BaseModel):
    telegram_id: int
    username: str
    phone: str
    password: str
    chat_id: int
    tg_username: str
    email: Optional[str] = None


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None


class BanStatusRequest(BaseModel):
    user_id: int
    is_banned: bool


class GetSimilarityUsersRequest(BaseModel):
    name: str
    is_executor: bool = False
