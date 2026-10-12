"""Simulated authentication dependency for the relationship manager (S03).

Per constitution.md, authentication is strictly simulated and does not connect
to real identity providers or bank IAM systems.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.config import SIMULATED_AUTH_TOKEN

security = HTTPBearer(auto_error=False)


VALID_TOKENS = {SIMULATED_AUTH_TOKEN, "dev-token"}


def require_manager_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
) -> str:
    """Validate the simulated bearer token.

    Returns the authenticated manager identifier on success.
    Raises HTTPException 401 with standard detail shape on failure.
    """
    if credentials is None or credentials.credentials not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": (
                    "Invalid or missing simulated Bearer token. "
                    "Provide header 'Authorization: Bearer <token>'."
                ),
            },
        )
    return "MGR-001"
