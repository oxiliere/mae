from typing import Optional
from datetime import datetime
from ninja import ModelSchema, Schema
from passport.models import Batch, Passport
from passport.enums import PassportStatus



class BatchDetailsSchema(ModelSchema):
    """
    Schema for retrieving full details of a Batch.
    Used for listing and detail endpoints.
    """

    class Meta:
        model = Batch
        fields = '__all__'


class BatchCreateSchema(ModelSchema):
    """
    Schema for creating a new Batch.
    Optional 'status' field allows setting initial state (default is Pending).
    """
    status: Optional[str]
    organization: Optional[int]

    class Meta:
        model = Batch
        fields = ['received_date', 'status', 'organization']


class BatchUpdateSchema(ModelSchema):
    """
    Schema for updating a Batch.
    All fields are optional to allow partial updates.
    """
    received_date: Optional[datetime]
    organization: Optional[int]
    status: Optional[str]

    class Meta:
        model = Batch
        fields = ['received_date', 'status', 'organization']


class BatchFilterSchema(Schema):
    """
    Schema for filtering Batch querysets.
    Fields are optional and used for dynamic search/filter.
    """
    received_date: Optional[datetime] = None
    status: Optional[str] = None
    organization: Optional[int] = None


class PassportDetailsSchema(ModelSchema):
    """
    Schema for retrieving full details of a Passport,
    including nested Batch information.
    """
    batch: BatchDetailsSchema

    class Meta:
        model = Passport
        fields = '__all__'


class PassportCreateSchema(ModelSchema):
    """
    Schema for creating a new Passport.
    Fields 'status' and 'published_at' are optional; 
    default values are applied if not provided.
    """
    status: Optional[str]
    published_at: Optional[datetime]

    class Meta:
        model = Passport
        fields = [
            'batch', 'code', 'coupon_id',
            'first_name', 'middle_name', 'last_name',
            'gender', 'status', 'published_at',
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "batch": 1,
                "code": "P-1234",
                "coupon_id": "C-5678",
                "first_name": "KIBANGULA",
                "middle_name": "MUSUYU",
                "last_name": "Prosper",
                "gender": "Male",
                "status": PassportStatus.DRAFT,  # default if not provided
                "published_at": "2025-11-12T12:00:00Z",
            }
        }


class PassportUpdateSchema(ModelSchema):
    """
    Schema for updating a Passport.
    All fields are optional to allow partial updates.
    """
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[str]
    status: Optional[str]
    published_at: Optional[datetime]
    taken_at: Optional[datetime]
    code: Optional[str]
    coupon_id: Optional[str]

    class Meta:
        model = Passport
        fields = [
            'first_name', 'middle_name', 'last_name',
            'gender', 'status', 'published_at',
            'taken_at', 'code', 'coupon_id',
        ]


class PassportFilterSchema(Schema):
    """
    Schema for filtering Passport querysets.
    All fields are optional and used for dynamic search/filter operations.
    """
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    status: Optional[str] = None
    published_at: Optional[datetime] = None
    taken_at: Optional[datetime] = None
    code: Optional[str] = None
    coupon_id: Optional[str] = None


class PassportStatusUpdateSchema(Schema):
    """
    Schema for partial update of Passport status.
    Only the 'status' field is required.
    """
    status: PassportStatus



class StatusUpdateSchema(Schema):
    status: str

