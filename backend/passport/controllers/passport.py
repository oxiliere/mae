from ninja_extra import (
    api_controller,
    http_post,
    http_put,
    http_patch,
    http_get,
    http_delete
)
from ninja_extra.permissions import IsAuthenticated
from ninja_extra.pagination import (
    paginate, 
    PageNumberPaginationExtra, 
    PaginatedResponseSchema
)
from ninja.errors import HttpError
from .base_controller import BaseController
from passport.services import PassportService, BatchService
from passport.schemas import (
    PassportDetailsSchema,
    PassportCreateSchema,
    PassportUpdateSchema,
    PassportFilterSchema,
    BatchDetailsSchema,
    BatchCreateSchema,
    BatchUpdateSchema,
    BatchFilterSchema,
    StatusUpdateSchema,
)
from passport.permissions import IsSameOrganizationMember



# -------------------------
# Passport Controller
# -------------------------
@api_controller(
    "/passports",
    tags=["Passports"],
    permissions=[IsAuthenticated & IsSameOrganizationMember()]
)
class PassportController(BaseController):
    """Controller for managing Passport resources."""

    def __init__(self, passport_serv: PassportService):
        super().__init__(passport_serv)
        self.list_schema = PassportDetailsSchema
        self.create_schema = PassportCreateSchema
        self.update_schema = PassportUpdateSchema
        self.filter_schema = PassportFilterSchema
        self.details_schema = PassportDetailsSchema
        self.filter_method = "search_and_filter_passports"


    @http_post("", response=PassportDetailsSchema)
    def create_item(self, request, data: PassportCreateSchema):
        """Create a new passport."""
        return self.service.create(**data.dict())


    @http_put("/{item_id}", response=PassportDetailsSchema)
    def update_item(self, request, item_id: int, data: PassportUpdateSchema):
        """Update an existing passport by ID."""
        return self.service.update(item_id, **data.dict(exclude_unset=True))


    @http_patch("/{item_id}/status", response=PassportDetailsSchema)
    def patch_status(self, request, item_id: int, data: StatusUpdateSchema):
        """Update the status of a passport."""
        return self.service.patch_status(item_id, status=data.status)


    @http_post("/{item_id}/publish", response=PassportDetailsSchema)
    def publish_item(self, request, item_id: int):
        """Publish a passport, setting its published timestamp."""
        passport = self.service.get(item_id)
        return self.service.publish(passport)


# -------------------------
# Batch Controller
# -------------------------
@api_controller(
    "/batches",
    tags=["Batches"],
    permissions=[IsAuthenticated & IsSameOrganizationMember()]
)
class BatchController(BaseController):
    """Controller for managing Batch resources and related passports."""

    def __init__(self, batch_serv: BatchService):
        super().__init__(batch_serv)
        self.list_schema = BatchDetailsSchema
        self.create_schema = BatchCreateSchema
        self.update_schema = BatchUpdateSchema
        self.filter_schema = BatchFilterSchema
        self.details_schema = BatchDetailsSchema
        self.filter_method = "search_and_filter_batches"


    @http_post("", response=BatchDetailsSchema)
    def create_item(self, request, data: BatchCreateSchema):
        """Create a new batch."""
        return self.service.create(**data.dict())


    @http_put("/{item_id}", response=BatchDetailsSchema)
    def update_item(self, request, item_id: int, data: BatchUpdateSchema):
        """Update an existing batch by ID."""
        return self.service.update(item_id, **data.dict(exclude_unset=True))


    @http_patch("/{item_id}/status", response=BatchDetailsSchema)
    def patch_status(self, request, item_id: int, data: StatusUpdateSchema):
        """Update the status of a batch."""
        return self.service.update(item_id, status=data.status)


    @http_post("/{item_id}/publish", response={"detail": str})
    def publish_batch(self, request, item_id: int, all: bool = True):
        """Publish all or completed passports in a batch."""
        success = self.service.publish(item_id, all=all)
        if not success:
            raise HttpError(400, "No passports to publish in this batch")
        return {"detail": "Batch published successfully"}


    @http_get(
        "/{batch_id}/passports", 
        response=PaginatedResponseSchema[PassportDetailsSchema]
    )
    @paginate(PageNumberPaginationExtra, page_size=20)
    def batch_passports(self, request, batch_id: int, **filters):
        """Get all passports of a batch with optional filters applied."""
        return self.service.get_passports(batch_id=batch_id, **filters)

