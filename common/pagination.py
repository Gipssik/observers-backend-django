from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class LimitSkipPagination(LimitOffsetPagination):
    offset_query_param = "skip"

    def get_paginated_response(self, data):
        return Response(data)
