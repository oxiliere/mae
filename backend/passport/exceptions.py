from ninja_extra.exceptions import APIException


class PassportNotFound(APIException):
    status_code = 404
    default_detail = "Passport not found"


class PassportConflict(APIException):
    status_code = 400
    default_detail = "Invalid passport data"

