from fastapi import Depends, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from starlette import status
from server.config import env_settings
from typing import Optional


class UnauthorizedMessage(BaseModel):
    detail: str = "Bearer token missing or unknown"


# We will handle a missing token ourselves
get_bearer_token = HTTPBearer(auto_error=False)


async def get_token(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> str:
    # Simulate a database query to find a known token
    if (
        auth is None
        or (token := auth.credentials) not in env_settings.KNOWN_ACCESS_TOKENS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UnauthorizedMessage().detail,
        )
    return token
