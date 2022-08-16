import functools
from urllib import parse as url_parse
from typing import Callable

from channels.db import database_sync_to_async
from channels.routing import URLRouter
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from authentication.models import User


def parse_query_string(query_string: str) -> dict[str, str]:
    """Parses query parameters from query string.

    :param query_string: Raw string of query parameters.
    :return: Dict with query parameters.
    """
    query_dict = url_parse.parse_qs(query_string)
    return {key: value[0] for key, value in query_dict.items()}


@database_sync_to_async
def authenticate(token: str | None) -> User | AnonymousUser:
    """Authenticates a user.

    If token is invalid or user does not exist, returns AnonymousUser.

    :param token: Token string.
    :return: Current user or AnonymousUser.
    """
    if not token:
        return AnonymousUser()

    token = token[7:]  # removes 'Bearer ' part.
    auth = JWTAuthentication()
    validated_token = auth.get_validated_token(token)
    try:
        return auth.get_user(validated_token)
    except (AuthenticationFailed, InvalidToken):
        return AnonymousUser()


class QueryAuthMiddleware:
    """Provides authentication from token in query params."""

    def __init__(self, app: URLRouter):
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: functools.partial):
        query_string: bytes = scope.get("query_string", "")
        params = parse_query_string(query_string.decode("utf-8"))
        token = params.get("token")
        scope["user"] = await authenticate(token)
        return await self.app(scope, receive, send)
