from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from database.database import async_session
from database.models import UserTicket, TicketStatus


async def create_user_ticket(
        user_id: int,
        description: str,
        subject: str
):
    try:
        async with async_session() as session:
            ticket = UserTicket(
                user_id=user_id,
                description=description,
                subject=subject
            )

            session.add(ticket)
            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()
        raise


async def get_user_tickets(
        status: TicketStatus = TicketStatus.open
):
    try:
        async with async_session() as session:

            res = await session.execute(
                select(UserTicket).where(UserTicket.status == status)
            )

            return res.scalars().all()

    except IntegrityError as err:
        print(err)
        raise


async def update_ticket_status(
        ticket_id: int,
        new_status: TicketStatus,
        admin_id: int
):
    try:
        async with async_session() as session:
            await session.execute(
                update(UserTicket).where(UserTicket.ticket_id == ticket_id).values(
                    status=new_status,
                    updated_at=datetime.utcnow(),
                    responded_by=admin_id,
                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()
        raise
