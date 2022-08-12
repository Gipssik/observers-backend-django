from rest_framework import status
from rest_framework.exceptions import APIException


class UnprocessableEntity(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unprocessable entity."
    default_code = "unprocessable_entity"
