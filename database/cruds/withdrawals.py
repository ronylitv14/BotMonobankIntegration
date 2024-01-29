import decimal
from datetime import datetime

from sqlalchemy import select, desc, update

from sqlalchemy.exc import IntegrityError

from database.database import async_session
from database.models import WithdrawalStatus, WithdrawalRequest


async def create_withdrawal_request(
        user_id: int,
        amount: decimal.Decimal,
        commission: decimal.Decimal,
        status: WithdrawalStatus,
        payment_method: str
):
    try:
        async with async_session() as session:
            session.add(
                WithdrawalRequest(
                    user_id=user_id,
                    amount=amount,
                    status=status,
                    payment_method=payment_method,
                    commission=commission
                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()
        raise


async def get_all_withdrawal_requests(
        status: WithdrawalStatus = WithdrawalStatus.pending
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(WithdrawalRequest)
                .where(WithdrawalRequest.status == status)
                .order_by(desc(WithdrawalRequest.request_date))
            )

            return res.scalars().all()

    except IntegrityError as err:
        print(err)
        return []


async def update_withdrawal_request(
        request_id: int,
        new_status: WithdrawalStatus,
        processed_time: datetime,
        admin_id: int
):
    try:
        async with async_session() as session:
            await session.execute(
                update(WithdrawalRequest).where(WithdrawalRequest.request_id == request_id).values(
                    status=new_status,
                    processed_date=processed_time,
                    admin_id=admin_id
                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()
        raise
