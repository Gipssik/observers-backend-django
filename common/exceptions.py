from rest_framework import status
from rest_framework.exceptions import APIException


class UnprocessableEntity(APIException):
    """Raises HTTP error with status code 422."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unprocessable entity."
    default_code = "unprocessable_entity"
