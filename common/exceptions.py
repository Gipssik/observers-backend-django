from rest_framework.exceptions import APIException


class UnprocessableEntity(APIException):
    status_code = 422
    default_detail = "Unprocessable entity."
    default_code = "unprocessable_entity"
