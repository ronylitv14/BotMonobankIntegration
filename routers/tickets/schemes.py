from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from database.models import TicketStatus


class UserTicketRequest(BaseModel):
    user_id: int
    description: str
    subject: str


class TicketStatusUpdateRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    new_status: TicketStatus
    admin_id: int

class UserTicketResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
    ticket_id: int
    user_id: int
    subject: str
    description: str
    status: TicketStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    response: Optional[str] = None
    responded_by: Optional[int] = None
