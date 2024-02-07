from typing import List

from sqlalchemy import select, update, and_
from sqlalchemy.exc import IntegrityError

from database.database import async_session
from database.models import TaskStatus, Task, Executor, User, FileType, ProfileStatus, Chat


async def get_executor_orders(
        executor_id: int,
        *status: TaskStatus
):
    try:
        async with async_session() as session:
            stmt = select(Task)\
                .join(Chat, Task.task_id == Chat.task_id)\
                .where(
                and_(
                    Chat.executor_id == executor_id,
                    Task.status.in_(status)
                )
            )

            orders = await session.execute(stmt)

            return orders.scalars().all()

    except IntegrityError:
        print("Error retrieving data!")
        await session.rollback()


async def get_executor(
        user_id: int
):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Executor).where(Executor.user_id == user_id)
            )

            return result.scalars().first()
    except IntegrityError:
        await session.rollback()
        print("Cant get executor!")


async def get_all_executors_profiles(*args):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User).join(Executor, User.telegram_id == Executor.user_id).where(
                    Executor.profile_state == ProfileStatus.accepted
                )
            )

            return result.scalars().all()
    except IntegrityError:
        print("Error with getting data!")
        await session.rollback()


async def create_executor_profile(
        user_id: int,
        description: str,
        work_examples: List[str],
        work_files_type: List[FileType],
        tags: List[str]

):
    try:
        async with async_session() as session:
            session.add(
                Executor(
                    user_id=user_id,
                    description=description,
                    work_examples=work_examples,
                    work_files_type=work_files_type,
                    tags=tags
                )
            )

            await session.commit()

    except IntegrityError:
        await session.rollback()
        print("Error with adding executor")
        raise


async def update_executor_application_status(
        executor_id: int,
        new_profile_state: ProfileStatus
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Executor).where(Executor.executor_id == executor_id).values(profile_state=new_profile_state)
            )

            await session.commit()

    except IntegrityError:
        await session.rollback()
        print("Wrong params for executor status updating")


async def get_executor_applications():
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Executor).where(Executor.profile_state == ProfileStatus.created)
            )
            return result.scalars().all()

    except IntegrityError:
        print("error")
        await session.rollback()
        raise
