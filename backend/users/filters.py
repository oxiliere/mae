from ninja import FilterSchema, Field
from typing import Optional


class UserFilterSchema(FilterSchema):
    is_active: Optional[bool] = Field(None, alias="is_active")
    search: Optional[str] = Field(None, q=[
        'email__icontains',
        'first_name__icontains',
        'last_name__icontains'
    ])
