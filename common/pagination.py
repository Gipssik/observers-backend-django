from typing import Any

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class LimitSkipPagination(LimitOffsetPagination):
    """Changes default `offset` label to 'skip'."""

    offset_query_param = "skip"

    def get_paginated_response(self, data: Any) -> Response:
        """Returns raw data without adding other fields.

        :param data: Response data.
        :return: Response with raw data.
        """
        return Response(data)
