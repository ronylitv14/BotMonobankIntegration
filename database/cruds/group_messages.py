from sqlalchemy import select

from sqlalchemy.exc import IntegrityError

from database.database import async_session
from database.models import GroupMessage


async def add_group_message(
        group_message_id: int,
        task_id: int,
        message_text: str,
        has_files: bool = False
):
    try:
        async with async_session() as session:
            group_message = GroupMessage(
                group_message_id=group_message_id,
                task_id=task_id,
                message_text=message_text,
                has_files=has_files
            )

            session.add(group_message)
            await session.commit()
            return True
    except IntegrityError:
        await session.rollback()
        print("IntegrityError: Violated a database constraint. group message added")

    return False


async def get_group_message(
        task_id: int
):
    try:
        async with async_session() as session:
            group_message = await session.execute(
                select(GroupMessage).where(GroupMessage.task_id == task_id)
            )
            group_message = group_message.scalars().first()
            return group_message
    except IntegrityError:
        print("Error with database acquired!")
