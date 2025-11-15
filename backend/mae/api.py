from django.core.exceptions import ValidationError
from django.http import HttpRequest
from ninja_extra import NinjaExtraAPI
from organisations.controllers import OrganizationController
from passport.controllers import (
    PassportController, 
    BatchController
)
from .security import (
    basic_auth
)



api = NinjaExtraAPI(
    title="Oxiliere Passport API",
    description="API for Oxiliere Passports",
    version="1.0.0",
    auth=[basic_auth],
)


api.register_controllers(
    OrganizationController,
    PassportController,
    BatchController,
)


@api.exception_handler(ValidationError)
def service_unavailable_handler(request: HttpRequest, exc: ValidationError):
    return api.create_response(
        request,
        {   
            "code": "validation_error",
            "detail": str(exc)
        },
        status=400,
    )

