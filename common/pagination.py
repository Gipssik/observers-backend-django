from rest_framework.pagination import LimitOffsetPagination


class LimitSkipPagination(LimitOffsetPagination):
    offset_query_param = "skip"
