from ninja_extra import (
    api_controller,
    http_post,
    http_put,
)
from ninja_extra.permissions import IsAuthenticated
from .base_controller import BasePassportController
from passport.services import (
    PassportService,
    BatchService,
)
from passport.schemas import (
    PassportDetailsSchema,
    PassportCreateSchema,
    PassportUpdateSchema,
    PassportFilterSchema,
    BatchDetailsSchema,
    BatchCreateSchema,
    BatchUpdateSchema,
    BatchFilterSchema,
)



@api_controller(
    "/passports",
    tags=["Passports"],
    permissions=[IsAuthenticated]
)
class PassportController(BasePassportController):

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
        return self.service.create(**data.dict())


    @http_put("/{item_id}", response=PassportDetailsSchema)
    def update_item(self, request, item_id: int, data: PassportUpdateSchema):
        return self.service.update(item_id, **data.dict(exclude_unset=True))



@api_controller(
    "/batches",
    tags=["Batches"],
    permissions=[IsAuthenticated]
)
class BatchController(BasePassportController):

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
        return self.service.create(**data.dict())


    @http_put("/{item_id}", response=BatchDetailsSchema)
    def update_item(self, request, item_id: int, data: BatchUpdateSchema):
        return self.service.update(item_id, **data.dict(exclude_unset=True))
