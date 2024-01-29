from decimal import Decimal

from config import verify_token

from fastapi import Security, status
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from routers.reviews.schemes import ReviewDataRequest, SightsResponse, UserReviewsResponse, CommentResponse
from database.cruds.reviews import save_review_data, get_user_reviews_data

reviews_router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    dependencies=[Security(verify_token)]
)


@reviews_router.post("/")
async def post_review_data(review_data: ReviewDataRequest):
    try:
        print(review_data)
        await save_review_data(**review_data.model_dump())
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@reviews_router.get("/{user_id}", response_model=UserReviewsResponse)
async def get_user_reviews(user_id: int):
    pos_data, neg_data, avg_rating, comments = await get_user_reviews_data(user_id)

    if not (pos_data and neg_data and avg_rating):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    positive_sights = [SightsResponse(username=item[0], reviewed_id=item[1], sight_title=item[2], count=item[3]) for
                       item in pos_data]
    negative_sights = [SightsResponse(username=item[0], reviewed_id=item[1], sight_title=item[2], count=item[3]) for
                       item in neg_data]
    comments = [CommentResponse(username=item[0], comment=item[1]) for item in comments]

    return UserReviewsResponse(
        pos_sights=positive_sights,
        neg_sights=negative_sights,
        avg_rating=round(Decimal(avg_rating), 2),
        comments=comments
    )
