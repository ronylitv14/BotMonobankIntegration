from pydantic import BaseModel, ConfigDict


class WarningData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    reason: str
    issued_by: int
    warning_count: int
