from ninja_extra import (
    ControllerBase, 
    http_get, 
    http_delete, 
    http_patch
)
from ninja_extra.pagination import (
    paginate, 
    PageNumberPaginationExtra, 
    PaginatedResponseSchema
)
from django.http import HttpRequest
from typing import Type, Any
from ninja.errors import HttpError



class BaseController(ControllerBase):
    """
    Generic controller for models like Passport and Batch.
    Provides list, retrieve, delete, and patch operations.
    Concrete controllers must override create_item and update_item
    so OpenAPI can correctly expose schemas.
    """

    service: Any
    list_schema: Type
    create_schema: Type
    update_schema: Type
    details_schema: Type
    filter_schema: Type
    filter_method: str = "search_and_filter_passports"

    def __init__(self, service: Any):
        """Initialize the controller with a specific service."""
        self.service = service


    @http_get(
        "", 
        response=PaginatedResponseSchema[Any]
    )
    @paginate(PageNumberPaginationExtra, page_size=20)
    def list_items(self, request: HttpRequest, **filters: Any):
        """
        List all items or filter them based on provided parameters.

        :param request: Django HttpRequest object.
        :param filters: Optional filtering parameters.
        :return: Paginated list of items matching the filters.
        """
        if self.filter_schema:
            schema_instance = self.filter_schema(**filters)
            filter_data = schema_instance.dict(exclude_unset=True)
        else:
            filter_data = filters

        method = getattr(self.service, self.filter_method)
        return method(**filter_data)


    @http_get(
        "/{item_id}",
    )
    def get_item(self, request: HttpRequest, item_id: int):
        """
        Retrieve a single item by its ID.

        :param request: Django HttpRequest object.
        :param item_id: ID of the item to retrieve.
        :return: The requested item.
        :raises HttpError: If item is not found.
        """
        obj = self.service.get(item_id)
        if not obj:
            raise HttpError(404, "Item not found")
        return obj


    @http_delete(
        "/{item_id}"
    )
    def delete_item(self, request: HttpRequest, item_id: int):
        """
        Delete an item by its ID.

        :param request: Django HttpRequest object.
        :param item_id: ID of the item to delete.
        :return: Success message.
        :raises HttpError: If item is not found.
        """
        deleted = self.service.delete(item_id)
        if not deleted:
            raise HttpError(404, "Item not found")
        return {"detail": "Deleted successfully"}



    @http_patch(
        "/{item_id}/status",
        url_name="passport_change"
    )
    def patch_item(self, request: HttpRequest, item_id: int, data: Any):
        """
        Update the status of an item.

        :param request: Django HttpRequest object.
        :param item_id: ID of the item to patch.
        :param data: Data object containing the new status.
        :return: Success message.
        :raises HttpError: If data is invalid or item is not found.
        """
        if not hasattr(data, "dict"):
            raise HttpError(400, "Invalid data schema")

        updated = self.service.patch_status(item_id, **data.dict())
        if not updated:
            raise HttpError(404, "Item not found")

        return {"detail": "Updated successfully"}
