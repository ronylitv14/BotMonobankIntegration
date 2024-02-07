from typing import List, Optional, Any, Dict, AnyStr
from datetime import datetime, timedelta

from aiogram.enums import ChatType

from sqlalchemy import select, update, and_, asc, or_
from sqlalchemy.exc import IntegrityError
from database.database import async_session

from database.models import Chat, User, Task


async def save_chat_data(
        chat_id: int,
        task_id: int,
        group_name: str,
        invite_link: str,
        participants_count: int,
        client_id: int,
        executor_id: int,
        chat_admin: str,
        supergroup_id: Optional[int] = None
):
    try:
        async with async_session() as session:
            chat = Chat(
                chat_id=chat_id,
                task_id=task_id,
                group_name=group_name,
                invite_link=invite_link,
                participants_count=participants_count,
                client_id=client_id,
                executor_id=executor_id,
                chat_admin=chat_admin,
                supergroup_id=supergroup_id,
                in_use=False
            )

            session.add(chat)
            await session.commit()

            return chat
    except IntegrityError as err:
        await session.rollback()
        print(err)
        print("Problems with saving chat")
        raise


async def get_chats_by_taskid(
        task_id: int
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Chat).where(
                    and_(
                        (Chat.task_id == task_id),
                        (Chat.active == True)
                    )
                )
            )

            return res.scalars().all()

    except IntegrityError:
        await session.rollback()


async def get_recent_clients(
        executor_id: int
) -> List[User]:
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .join(Task, Task.client_id == User.telegram_id)
                .where(Task.executor_id == executor_id)
            )

            return result.scalars().all()

    except IntegrityError:
        await session.rollback()


async def get_chat_object(
        chat_id: Optional[int] = None,
        db_chat_id: Optional[int] = None,
        supergroup_id: Optional[int] = None
) -> Chat:
    try:
        async with async_session() as session:

            if not any([chat_id, db_chat_id, supergroup_id]):
                raise ValueError("chat_id or db_chat_id has to be specified!")

            if db_chat_id:
                res = await session.execute(
                    select(Chat).where(Chat.id == db_chat_id)
                )
                return res.scalars().first()

            if supergroup_id:
                res = await session.execute(
                    select(Chat).where(Chat.supergroup_id == supergroup_id)
                )
                return res.scalars().first()

            res = await session.execute(
                select(Chat).where(Chat.chat_id == chat_id)
            )

            return res.scalars().first()

    except IntegrityError as err:
        print(err)
        await session.rollback()
        raise


async def update_chat_type(
        chat_type: ChatType,
        supergroup_id: int,
        db_chat_id
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Chat).where(Chat.id == db_chat_id).values(
                    chat_type=chat_type,
                    supergroup_id=supergroup_id
                )
            )

            await session.commit()
    except IntegrityError as err:
        print("Failed saving")
        print(err)
        raise


async def get_all_user_chats(
        client_id: int
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Chat).where(
                    and_(
                        Chat.client_id == client_id,
                        Chat.active == True,
                        Chat.in_use == False
                    )
                ).order_by(asc(Chat.id))
            )

            return res.scalars().all()

    except IntegrityError:
        print("Get all users")
        raise


async def _update_chat_field(
        db_chat_id: int,
        field_name: str,
        field_value: Any
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Chat).where(
                    Chat.id == db_chat_id
                ).values(**{field_name: field_value})
            )

            await session.commit()
    except Exception as err:
        await session.rollback()


async def update_group_title(
        db_chat_id,
        group_name
):
    await _update_chat_field(db_chat_id, "group_name", group_name)


async def update_chat_fields(db_chat_id: int, fields: Dict[AnyStr, Any]):
    try:
        async with async_session() as session:
            await session.execute(
                update(Chat).where(Chat.id == db_chat_id).values(
                    **fields
                )
            )

            await session.commit()

    except Exception as err:
        await session.rollback()


async def get_unused_chats(hours: int = 12):
    async with async_session() as session:
        stmt = select(Chat).where(
            or_(
                and_(
                    (Chat.in_use == False),
                    (datetime.utcnow() - Chat.payment_date) > timedelta(hours=hours),
                    (Chat.active == True)
                ),
                and_(
                    Chat.in_use == False,
                    Chat.active == False
                )
            )

        ).order_by(asc(Chat.payment_date))

        chats = await session.execute(stmt)

        return chats.scalars().all()


async def check_chat_existence(
        task_id: int,
        executor_id: int,
        client_id: int
):
    async with async_session() as session:
        chat = await session.execute(
            select(Chat).where(
                and_(
                    (Chat.task_id == task_id),
                    (Chat.executor_id == executor_id),
                    (Chat.client_id == client_id),
                    (Chat.active == True),
                )
            )
        )

        return True if chat.scalars().all() else False
