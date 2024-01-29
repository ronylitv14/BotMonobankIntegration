import datetime
import enum
from typing import List, Optional

from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError, NoResultFound

from database.database import async_session
from database.models import TaskStatus, FileType, PropositionBy, Task, User


class UserType(enum.StrEnum):
    client: str = "client"
    executor: str = "executor"


async def save_task_to_db(
        client_id: int,
        status: TaskStatus,
        price: str,
        subjects: List[str],
        work_type: List[str],
        deadline: datetime.date,
        files: List[str] = None,
        files_type: List[FileType] = None,
        description: str = "",
        proposed_by=PropositionBy.public,
        executor_id: Optional[int] = None
):
    try:
        async with async_session() as session:
            print(proposed_by)
            task = Task(
                client_id=client_id,
                status=status,
                price=price,
                deadline=deadline,
                files=files,
                files_type=files_type,
                subjects=subjects,
                description=description,
                work_type=work_type,
                proposed_by=proposed_by,
                executor_id=executor_id
            )

            session.add(task)
            await session.commit()
            return task
    except AttributeError:
        await session.rollback()
        print("Incorrect input data!")
        raise
    except IntegrityError as err:
        await session.rollback()
        print(f"Database error!: {err}")
        raise


async def update_task_status(
        task_id: int,
        status: TaskStatus
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Task).where((Task.task_id == task_id)).values(status=status)
            )

            await session.commit()

            return True
    except IntegrityError:
        await session.rollback()
        print("IntegrityError: Violated a database constraint. task updated")

    return False


async def get_all_tasks(
        user_id: int,
        user_type: UserType,
        *status: TaskStatus,
        task_id: Optional[int] = None
):
    try:
        async with async_session() as session:
            if user_type == UserType.client:
                default_stmt = select(Task).where(
                    (Task.client_id == user_id) & (Task.status.in_(status))
                )

            if user_type == UserType.executor:
                default_stmt = select(Task).where(
                    (Task.executor_id == user_id) & (Task.status.in_(status))
                )

            if task_id:
                default_stmt.where(
                    Task.task_id == task_id
                )

            orders = await session.execute(default_stmt)

            orders = orders.scalars().all()
            return orders
    except IntegrityError:
        print("Error with database acquired!")
        raise


async def get_user_by_task_id(task_id: int):
    try:
        async with async_session() as session:
            stmt = (
                select(User)
                .select_from(User)
                .join(Task, User.telegram_id == Task.client_id)
                .where(Task.task_id == task_id)
            )

            result = await session.execute(stmt)
            user = result.scalars().first()
            return user

    except IntegrityError:
        await session.rollback()
        print("Error with getting user")


async def get_proposed_deals(
        proposed_by: PropositionBy,
        user_id: int
) -> List[Task]:
    try:
        async with async_session() as session:

            if proposed_by == PropositionBy.client:
                # executor: Executor = await get_executor(user_id)

                result = await session.execute(
                    select(Task).where(
                        (Task.proposed_by == proposed_by) & (Task.status == TaskStatus.active) & (
                                Task.executor_id == user_id)
                    )
                )
                return result.scalars().all()

            result = await session.execute(
                select(Task).where(
                    (Task.proposed_by == proposed_by) & (Task.status == TaskStatus.active) & (
                            Task.client_id == user_id)
                )
            )

            return result.scalars().all()

    except IntegrityError:
        print("Couldnt get data back")
        await session.rollback()


async def get_task(task_id: int):
    try:
        async with async_session() as session:
            task = await session.execute(
                select(Task).where(Task.task_id == task_id)
            )
            task = task.scalars().first()
            return task
    except NoResultFound:
        return []