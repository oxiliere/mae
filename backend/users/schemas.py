from typing import Optional
from uuid import UUID
from ninja import Schema
from utils_mixins.types import EmailApiType



class UserSchema(Schema):
    """Schema for serializing and deserializing User objects"""
    email: EmailApiType
    password: str
    first_name: str
    last_name: str


class OrganisationBasicSchema(Schema):
    """Schéma simplifié pour l'organisation"""
    id: UUID
    name: str
    slug: Optional[str]

