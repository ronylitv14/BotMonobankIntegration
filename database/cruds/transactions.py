import decimal
from sqlite3 import IntegrityError
from typing import Optional

from sqlalchemy import update, select, or_, and_
from database.cruds.balance import update_balance, BalanceAction

from database.database import async_session
from database.models import TransactionType, TransactionStatus, Transaction


async def add_transaction_data(
        invoice_id: str,
        amount: decimal.Decimal,
        transaction_type: TransactionType,
        transaction_status: TransactionStatus,
        sender_id: Optional[int] = None,
        receiver_id: Optional[int] = None,
        task_id: Optional[int] = None,
        commission: Optional[decimal.Decimal] = None
):
    try:
        async with async_session() as session:
            session.add(
                Transaction(
                    invoice_id=invoice_id,
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_status=transaction_status,
                    task_id=task_id,
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    commission=commission
                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        print("Transaction error")
        await session.rollback()
        raise


async def update_transaction_status(
        invoice_id: str,
        new_status: TransactionStatus
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Transaction).where(Transaction.invoice_id == invoice_id).values(transaction_status=new_status)
            )

            await session.commit()

    except IntegrityError:
        await session.rollback()
        raise


async def get_user_transactions(
        user_id: int
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Transaction).where(or_(Transaction.receiver_id == user_id, Transaction.sender_id == user_id))
            )

            return res.scalars().all()

    except IntegrityError:
        print("Error")
        return []


async def get_transaction_data(
        sender_id: int,
        receiver_id: int,
        task_id: Optional[int] = None,
        transaction_type: Optional[TransactionType] = None,
        transaction_status: Optional[TransactionStatus] = None
):
    async with async_session() as session:

        conditions = [
            (Transaction.sender_id == sender_id),
            (Transaction.receiver_id == receiver_id),
        ]

        if task_id is not None:
            conditions.append(Transaction.task_id == task_id)
        if transaction_type is not None:
            conditions.append(Transaction.transaction_type == transaction_type)
        if transaction_status is not None:
            conditions.append(Transaction.transaction_status == transaction_status)

        res = await session.execute(
            select(Transaction).where(
                and_(
                    *conditions
                )
            )
        )

        return res.scalars().all()


async def save_monobank_transaction_data(transaction_status, payload, user_id: int):
    if transaction_status == 'success':
        await update_transaction_status(
            invoice_id=payload.get('invoiceId'),
            new_status=TransactionStatus.completed
        )

        amount = decimal.Decimal(payload.get('amount')) / 100

        await update_balance(
            user_id=user_id,
            amount=amount,
            action=BalanceAction.replenishment
        )

    elif transaction_status == 'failure':
        await update_transaction_status(
            invoice_id=payload.get("invoiceId"),
            new_status=TransactionStatus.failed
        )
