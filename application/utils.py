import os
import json

from configparser import ConfigParser
from typing import Dict
from urllib.request import urlopen

from jose import jwt


def set_up() -> dict:
    """Sets up configuration for the app"""

    env = os.getenv("ENV", ".config")

    if env == ".config":
        config = ConfigParser()
        config.read(".config")
        config = config["AUTH0"]
    else:
        config = {
            "DOMAIN": os.getenv("DOMAIN", "your.domain.com"),
            "API_AUDIENCE": os.getenv("API_AUDIENCE", "your.audience.com"),
            "ALGORITHMS": os.getenv("ALGORITHMS", "RS256"),
        }
    return config


class AuthError(Exception):
    """Formats error response and append status code."""
    def __init__(self, error: Dict[str, str], status_code: int):
        super().__init__()
        self.error = error
        self.status_code = status_code


def requires_scope(required_scope: str, token: str) -> dict:
    """Determines if the required scope is present in the access token

    Args:
        required_scope (str): The scope required to access the resource
        token (str): The JWT token to get claims from

    Returns:
        This returns the unverified claims of the token when the required scope
        is present
    """
    unverified_claims = jwt.get_unverified_claims(token)

    if "scope" not in unverified_claims:
        payload = {
            "code": "missing_scope",
            "description": "No scopes found in token"
        }
        raise AuthError(payload, 404)

    token_scopes = unverified_claims["scope"].split()
    if required_scope in token_scopes:
        return unverified_claims

    payload = {
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }
    raise AuthError(payload, 401)


def validate_token(token: str, config: dict):
    """Validates an Access Token
    
    Args:
        token (str): Access token to validate
        config (dict): A dictionary containing the following keys
            - 'DOMAIN' for the Auth0 Domain
            - 'ALGORITHMS' for the JWT algorithm (usually RS256)
            - 'API_AUDIENCE' the API identifier in Auth0
    """
    # Let's find our publicly available public keys,
    # which we'll use to validate the token's signature
    jsonurl = urlopen("https://" + config["DOMAIN"] + "/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())

    # We will parse the token and get the header for later use
    unverified_header = jwt.get_unverified_header(token)

    # Check if the token has a key ID
    if "kid" not in unverified_header:
        payload = {
            "code": "missing_kid",
            "description": "No kid found in token"
        }
        raise AuthError(payload, 401)

    try:
        # Check if we have a key with the key ID specified
        # from the header available in our list of public keys
        rsa_key = next(
            key for key in jwks["keys"]
            if key["kid"] == unverified_header["kid"]
        )

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=config["ALGORITHMS"],
                audience=config["API_AUDIENCE"],
                issuer="https://" + config["DOMAIN"] + "/",
            )
            # _request_ctx_stack.top.current_user = payload

        # The token is not valid if the expiry date is in the past
        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "Token is expired"},
                401
            )

        # The token should be issued by our Auth0 tenant,
        # and to be used with our API (Audience)
        except jwt.JWTClaimsError:
            payload = {
                "code": "invalid_claims",
                "description":
                    "Incorrect claims, please check the audience and issuer",
            }
            raise AuthError(payload, 401)

        # The token's signature is invalid
        except jwt.JWTError:
            payload = {
                "code": "invalid_signature",
                "description": "The signature is not valid",
            }
            raise AuthError(payload, 401)

        # Something went wrong parsing the JWT
        except Exception:
            payload = {
                "code": "invalid_header",
                "description": "Unable to parse authentication token.",
            }
            raise AuthError(payload, 401)

    except StopIteration:
        # We did not find the key with the ID specified in the token's header
        # in the list of available public keys for our Auth0 tenant.
        payload = {
            "code": "invalid_header",
            "description": "No valid public key found to validate signature.",
        }
        raise AuthError(payload, 401)


def requires_auth(token: str):
    """Determines if there is a valid Access Token available
    
    Args:
        token (str): Access token to validate
    """
    try:
        # Validate the token
        validate_token(token)
    except AuthError as error:
        # Abort the request if something went wrong fetching the token
        # or validating the token.
        # We return the status from the raised error,
        # and return the error as a json response body
        return json.dumps({"msg": error.error,
                           "status_code": error.status_code})
