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


class VerifyToken():
    """Does all the token verification using PyJWT"""

    def __init__(self, token, permissions=None, scopes=None):
        self.token = token
        self.permissions = permissions
        self.scopes = scopes
        self.config = get_config()

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f'https://{self.config.domain}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try: 
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config.algorithms,
                audience=self.config.api_audience,
                issuer=self.config.issuer,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        if self.scopes:
            result = self._check_claims(payload, 'scope', str, self.scopes.split(' '))
            if result.get("error"):
                return result

        if self.permissions:
            result = self._check_claims(payload, 'permissions', list, self.permissions)
            if result.get("error"):
                return result

        return payload

    def _check_claims(self, payload, claim_name, claim_type, expected_value):

        instance_check = isinstance(payload[claim_name], claim_type)
        result = {"status": "success", "status_code": 200}

        payload_claim = payload[claim_name]

        if claim_name not in payload or not instance_check:
            result["status"] = "error"
            result["status_code"] = 400

            result["code"] = f"missing_{claim_name}"
            result["msg"] = f"No claim '{claim_name}' found in token."
            return result

        if claim_name == 'scope':
            payload_claim = payload[claim_name].split(' ')

        for value in expected_value:
            if value not in payload_claim:
                result["status"] = "error"
                result["status_code"] = 403

                result["code"] = f"insufficient_{claim_name}"
                result["msg"] = (f"Insufficient {claim_name} ({value}). You "
                                  "don't have access to this resource")
                return result
        return result
