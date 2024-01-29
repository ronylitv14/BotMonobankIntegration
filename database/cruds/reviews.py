import asyncio
import decimal
from typing import List, Tuple

from sqlalchemy import select, func, desc
from sqlalchemy.exc import DBAPIError, IntegrityError

from database.database import async_session
from database.models import Review, User


async def save_review_data(
        reviewer_id: int,
        reviewed_id: int,
        task_id: int,
        rating: int,
        comment: str = None,
        positive_sights: List[str] = None,
        negative_sights: List[str] = None
):
    try:
        async with async_session() as session:

            review = Review(
                reviewer_id=reviewer_id,
                task_id=task_id,
                reviewed_id=reviewed_id,
                comment=comment,
                negative_sights=negative_sights,
                positive_sights=positive_sights,
                rating=rating
            )

            print(Review)

            session.add(review)
            await session.commit()
    except IntegrityError as err:
        print(err)
        await session.rollback()


async def get_user_reviews_data(
        user_id: int
) -> Tuple[List[Tuple], List[Tuple], decimal.Decimal, List[Tuple]]:
    async with (async_session() as session):
        positive_sights_unnest = select(
            User.username, Review.reviewed_id, func.unnest(Review.positive_sights).label("unnest_p_sights"),
            func.count(Review.reviewed_id).label("count"),
        ).join(User, User.telegram_id == Review.reviewed_id).where(
            Review.reviewed_id == user_id).group_by(
            Review.reviewed_id, "unnest_p_sights",
            User.username
        ).order_by(desc("count")).limit(3)

        negative_sights_unnest = select(
            User.username, Review.reviewed_id, func.unnest(Review.negative_sights).label("unnest_n_sights"),
            func.count(Review.reviewed_id).label("count")
        ).join(User, User.telegram_id == Review.reviewed_id).where(
            Review.reviewed_id == user_id).group_by(
            Review.reviewed_id, "unnest_n_sights",
            User.username
        ).order_by(desc("count")).limit(3)

        comments = select(
            User.username,
            Review.comment,
            func.avg(Review.rating).over()
        ).join(User, User.telegram_id == Review.reviewer_id
               ).where(
            Review.reviewed_id == user_id,
            Review.comment != None
        )

        avg_rating = select(func.avg(Review.rating)).where(Review.reviewed_id == user_id)

        pos = await session.execute(positive_sights_unnest)
        neg = await session.execute(negative_sights_unnest)
        rating = await session.execute(avg_rating)
        comments = await session.execute(comments)

        return pos.fetchall(), neg.fetchall(), rating.scalars().one(), comments.fetchall()
