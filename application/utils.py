import os
import jwt

from configparser import ConfigParser
from functools import cache
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Scheme for the Authorization header
token_auth_scheme = HTTPBearer()


@dataclass(frozen=True)
class MyConfig:
    domain: str
    api_audience: str
    issuer: str
    algorithms: str


@cache
def get_config():
    """Sets up configuration for the app"""
    env = os.getenv("ENV", ".config")
    config = ConfigParser()
    config.read(env)
    config = config["AUTH0"]
    return MyConfig(
        config["DOMAIN"], config["API_AUDIENCE"], config["ISSUER"], config["ALGORITHMS"]
    )


@cache
def get_jwks(config: Annotated[MyConfig, Depends(get_config)]):
    # This gets the JWKS from a given URL and does processing so you can
    # use any of the keys available
    return jwt.PyJWKClient(f"https://{config.domain}/.well-known/jwks.json")


def verify_jwt(
    token: Annotated[HTTPAuthorizationCredentials, Depends(token_auth_scheme)],
    jwks_client: Annotated[jwt.PyJWKClient, Depends(get_jwks)],
    config: Annotated[MyConfig, Depends(get_config)],
):
    try:
        # This gets the 'kid' from the passed token
        signing_key = jwks_client.get_signing_key_from_jwt(token.credentials).key
    except jwt.exceptions.PyJWKClientError as error:
        raise HTTPException(status_code=400, detail=error.__str__())
    except jwt.exceptions.DecodeError as error:
        raise HTTPException(status_code=400, detail=error.__str__())

    try:
        payload = jwt.decode(
            token.credentials,
            signing_key,
            algorithms=config.algorithms,
            audience=config.api_audience,
            issuer=config.issuer,
        )
    except Exception as error:
        raise HTTPException(status_code=403, detail=error.__str__())

    return payload


def verify_scope(token, scopes):
    _check_claims(token, "scope", str, scopes.split(" "))


def verify_permissions(token, permissions):
    _check_claims(token, "permissions", list, permissions)


def _check_claims(token, claim_name, claim_type, expected_value):
    if claim_name not in token or not isinstance(token[claim_name], claim_type):
        raise HTTPException(
            status_code=400, detail=f"No claim '{claim_name}' found in token."
        )

    token_claim = token[claim_name]

    if claim_name == "scope":
        token_claim = token[claim_name].split(" ")

    for value in expected_value:
        if value not in token_claim:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient {claim_name} ({value}). You don't have access to this resource.",
            )
