from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from database.database import async_session
from database.models import Warning, User


async def create_user_warning(
        user_id: int,
        reason: str,
        admin_id: int,
        warning_count: int
):
    try:
        async with async_session() as session:
            obj = Warning(
                user_id=user_id,
                reason=reason,
                issued_by=admin_id
            )

            session.add(obj)

            await session.execute(
                update(User).where(User.telegram_id == user_id).values(warning_count=warning_count + 1)
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()
