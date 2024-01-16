from fastapi import Security, status, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.exc import IntegrityError
from config import verify_token
from database.crud import create_user_warning
from routers.warnings.schemes import WarningData

warnings_router = APIRouter(
    prefix="/warnings",
    tags=["warnings"],
    dependencies=[Security(verify_token)]
)


@warnings_router.post("/")
async def create_user_warning(warning_data: WarningData):
    try:
        await create_user_warning(**warning_data.model_dump())
    except IntegrityError as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error with saving warning data!")
