import decimal
from datetime import datetime
from typing import Optional, List, Tuple

from pydantic import BaseModel, ConfigDict, condecimal


class ReviewDataRequest(BaseModel):
    reviewer_id: int
    reviewed_id: int
    task_id: int
    rating: int
    positive_sights: Optional[List[str]] = None
    negative_sights: Optional[List[str]] = None
    comment: Optional[str] = None


class SightsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    reviewed_id: int
    sight_title: str
    count: int


class CommentResponse(BaseModel):
    username: str
    comment: Optional[str] = None


class UserReviewsResponse(BaseModel):
    pos_sights: List[SightsResponse]
    neg_sights: List[SightsResponse]
    avg_rating: condecimal(decimal_places=2)
    comments: List[CommentResponse]
