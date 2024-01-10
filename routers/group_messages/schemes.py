import datetime
from typing import List, Optional
from database.models import TaskStatus

from pydantic import BaseModel, ConfigDict


class GroupMessageRequest(BaseModel):
    group_message_id: int
    task_id: int
    message_text: str
    has_files: bool = False


class GroupMessageResponse(GroupMessageRequest):
    model_config = ConfigDict(from_attributes=True)
    date_added: datetime.datetime
