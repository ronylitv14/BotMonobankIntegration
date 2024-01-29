import os
from typing import Annotated

from fastapi import Header, HTTPException, status
from fastapi.security import APIKeyHeader

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "token"
api_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def verify_token(token: Annotated[str | None, Header()]):
    if token == API_KEY:
        return True
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No token provided or it is incorrect!")
