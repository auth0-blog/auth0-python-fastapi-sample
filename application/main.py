"""Python FastAPI Auth0 integration example
"""

import json

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from .utils import requires_auth, requires_scope, AuthError, set_up


# Scheme for the Authorization header
token_auth_scheme = HTTPBearer()

# Creates app instance
app = FastAPI()


# API routes
@app.get("/api/public")
def public():
    """No access token required to access this route"""

    response = {"msg": ("Hello from a public endpoint!"
                        "You don't need to be authenticated to see this.")}
    return json.dumps(response)


@app.get("/api/private")
def private(token: str = Depends(token_auth_scheme)):
    """A valid access token is required to access this route"""

    configuration_dict = set_up()
    result = requires_auth(token.credentials, configuration_dict)
    if not result:
        response = {"msg": ("Hello from a private endpoint! "
                            "You need to be authenticated to see this.")}
        return json.dumps(response)
    return result


@app.get("/api/private-scoped")
def private_scoped(token: str = Depends(token_auth_scheme)):
    """A valid access token and an appropriate scope are required to access
    this route
    """
    try:
        claims = requires_scope("read:messages", token.credentials)
        if claims:
            response = {"msg": ("Hello from a private endpoint! "
                                "You need to be authenticated and have a "
                                "scope of read:messages to see this.")}
            return json.dumps(response)
    except AuthError as error:
        # return the error as a json response body
        return json.dumps({"msg": error.error,
                           "status_code": error.status_code})
