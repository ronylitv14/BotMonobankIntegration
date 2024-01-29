import decimal
from datetime import datetime
from uuid import uuid1

from sqlalchemy.exc import IntegrityError

from sqlalchemy import select, update, and_

from database.database import async_session, COMMISSION
from database.models import Transaction, TransactionStatus, Task, TaskStatus, Balance, TransactionType, Chat


async def check_successful_payment(
        task_id,
        receiver_id,
        sender_id
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Transaction).where(
                    (Transaction.task_id == task_id) & (Transaction.sender_id == sender_id) & (
                            Transaction.receiver_id == receiver_id)
                )
            )

            return True if res.scalars().all() else False
    except IntegrityError as err:
        print(err)
        await session.rollback()


async def accept_done_offer(
        transaction_id,
        task_id,
        receiver_id,
):
    try:
        async with async_session() as session:

            transaction = await session.execute(
                select(Transaction).where(Transaction.transaction_id == transaction_id)
            )

            transaction = transaction.scalars().first()
            transaction.transaction_status = TransactionStatus.completed

            await session.execute(
                update(Task).where(Task.task_id == task_id).values(
                    status=TaskStatus.done
                )
            )

            await session.execute(
                update(Chat).where(
                    and_(
                        Chat.task_id == task_id,
                        Chat.executor_id == transaction.receiver_id,
                        Chat.client_id == transaction.sender_id
                    )
                ).values(
                    is_payed=True,
                    payment_date=datetime.utcnow()
                )
            )

            receiver_balance = await session.execute(
                select(Balance).where(Balance.user_id == receiver_id)
            )

            receiver_balance: Balance = receiver_balance.scalars().first()
            receiver_balance.balance_money += transaction.amount

            await session.commit()

    except IntegrityError as err:
        await session.rollback()
        raise


async def create_money_transfer(
        receiver_id: int,
        sender_id: int,
        task_id: int,
        amount: decimal.Decimal
):
    try:
        async with async_session() as session:

            sender_balance = await session.execute(
                select(Balance).where(Balance.user_id == sender_id)
            )

            sender_balance = sender_balance.scalars().first()

            if sender_balance.balance_money < amount:
                raise ValueError("Incorrect transaction amount")

            commission = amount * COMMISSION

            amount_after_commission = amount - commission
            sender_balance.balance_money -= amount

            transaction = Transaction(
                task_id=task_id,
                invoice_id=str(uuid1()),
                transaction_type=TransactionType.transfer,
                receiver_id=receiver_id,
                sender_id=sender_id,
                transaction_status=TransactionStatus.pending,
                commission=commission,
                amount=amount_after_commission
            )

            session.add(transaction)

            await session.execute(
                update(Task).where(Task.task_id == task_id).values(
                    executor_id=receiver_id,
                    status=TaskStatus.executing
                )
            )

            await session.commit()
            return transaction
    except IntegrityError as err:
        print(err)
        await session.rollback()
        raise
