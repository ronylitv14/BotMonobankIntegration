from typing import List

from sqlalchemy import select, update, or_, delete

from sqlalchemy.exc import IntegrityError, DataError, InvalidRequestError
from sqlalchemy.sql.expression import func

from database.database import async_session
from database.models import User, UserStatus, Executor


async def get_user_auth(telegram_id: int) -> User:
    try:
        async with async_session() as session:
            res = await session.execute(select(User).where(User.telegram_id == telegram_id))

        return res.scalars().first()
    except IntegrityError as err:
        print(err)


async def delete_user_from_db(
        user_id: int
):
    try:
        async with async_session() as session:
            await session.execute(
                delete(User).where(User.telegram_id == user_id)
            )
            await session.commit()
    except IntegrityError:
        await session.rollback()
        raise


async def save_user_to_db(
        telegram_id: int,
        username: str,
        phone: str,
        password: str,
        chat_id: int,
        tg_username: str,
        email: str = "",
):
    try:
        async with async_session() as session:
            user = User(
                tg_id=telegram_id,
                username=username,
                phone=phone,
                email=email,
                password=password,
                chat_id=chat_id,
                tg_username=tg_username
            )

            session.add(user)
            await session.commit()
            await session.close()
        return True
    except IntegrityError:
        await session.rollback()
        print("IntegrityError: Violated a database constraint.")
    except DataError:
        await session.rollback()
        print("DataError: Invalid data type or value.")
    except InvalidRequestError:
        await session.rollback()
        print("InvalidRequestError: The session is in an invalid state.")


async def _update_user_field(user_id: int, field_name: str, value: str) -> None:
    """
    Update a specific field for a user in the database.

    Parameters:
    - user_id: The ID of the user.
    - field_name: The name of the field to update.
    - value: The new value for the field.

    Returns:
    None
    """
    try:
        async with async_session() as session:
            await session.execute(update(User).where((User.telegram_id == user_id)).values(**{field_name: value}))
            await session.commit()

    except IntegrityError:
        await session.rollback()
        print(f"IntegrityError: Violated a database constraint while updating {field_name}.")


async def update_user_email(
        user_id: int,
        email: str
):
    await _update_user_field(user_id, "email", email)


async def update_user_nickname(
        user_id: int,
        nickname: str
):
    await _update_user_field(user_id, "username", nickname)


async def update_user_phone(
        user_id: int,
        phone: str
):
    await _update_user_field(user_id, "phone", phone)


async def get_default_users():
    try:
        async with async_session() as session:

            result = await session.execute(
                select(User).where(~User.user_status.in_([UserStatus.superuser]))
            )
            return result.scalars().all()

    except IntegrityError:
        print("Error with results")


async def update_ban_status(
        user_id: int,
        is_banned: bool
):
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.telegram_id == user_id).values(is_banned=is_banned)
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()


async def get_similarity_users(
        name: str,
        is_executor: bool = False

) -> List[User]:
    try:
        async with async_session() as session:
            default_stmt = (select(User)
                            .where(or_((func.word_similarity(User.username, name) > 0.25),
                                       func.word_similarity(User.telegram_username, name) > 0.25))
                            .where(~User.user_status.in_([UserStatus.admin])))

            if is_executor:
                default_stmt = default_stmt.where(User.telegram_id.in_(select(Executor.user_id)))
            res = await session.execute(default_stmt)

        return res.scalars().all()

    except IntegrityError as err:
        print(err)
