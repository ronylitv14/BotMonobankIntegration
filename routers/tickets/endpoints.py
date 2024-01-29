from typing import List
from fastapi import status
from fastapi import Security
from config import verify_token
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from database.cruds.tickets import create_user_ticket, get_user_tickets, update_ticket_status
from routers.tickets.schemes import UserTicketRequest, TicketStatusUpdateRequest, UserTicketResponse
from database.models import TicketStatus
from sqlalchemy.exc import IntegrityError

tickets_router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    dependencies=[Security(verify_token)]
)


# Endpoint to create a user ticket
@tickets_router.post("/")
async def create_ticket(request: UserTicketRequest):
    try:
        await create_user_ticket(**request.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save ticket")

    return JSONResponse(content={"message": "User ticket created successfully."}, status_code=status.HTTP_201_CREATED)


# Endpoint to get user tickets by status
@tickets_router.get("/", response_model=List[UserTicketResponse])
async def get_tickets(ticket_status: TicketStatus):
    tickets = await get_user_tickets(status=ticket_status)
    if not tickets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tickets found")
    return tickets


# Endpoint to update a ticket's status
@tickets_router.patch("/{ticket_id}")
async def update_ticket(ticket_id: int, request: TicketStatusUpdateRequest):
    try:
        await update_ticket_status(ticket_id, request.new_status, request.admin_id)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Data can not be updated!")
    return JSONResponse(content={"message": "Ticket status updated successfully."}, status_code=status.HTTP_200_OK)
