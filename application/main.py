"""Python FastAPI Auth0 integration example
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Response
from fastapi.security import HTTPBearer

from .utils import verify_jwt, verify_scope


# Scheme for the Authorization header
token_auth_scheme = HTTPBearer()

# Creates app instance
app = FastAPI()


@app.get("/api/public")
def public():
    """No access token required to access this route"""

    result = {
        "status": "success",
        "msg": (
            "Hello from a public endpoint! You don't need to be "
            "authenticated to see this."
        ),
    }
    return result


@app.get("/api/private")
def private(response: Response, token: Annotated[dict, Depends(verify_jwt)]):
    """A valid access token is required to access this route"""
    return token


@app.get("/api/private-scoped")
def private_scoped(response: Response, token: Annotated[dict, Depends(verify_jwt)]):
    """A valid access token and an appropriate scope are required to access
    this route
    """
    verify_scope(token, "read:messages")
    return token
