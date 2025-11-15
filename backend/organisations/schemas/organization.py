from typing import Optional
from datetime import datetime
from ninja import ModelSchema, Schema, Field
from users.schemas import UserSchema
from organisations.models import (
    Organization,
    OrganizationUser,
)
from organisations.enums import MemberEnum



class PasswordSchema(Schema):
    password: str
    password1: str


class OrganizationSchema(ModelSchema):
    created_at: datetime = Field(..., alias="created")
    updated_at: datetime = Field(..., alias="modified")
    role: Optional[MemberEnum] = None

    @staticmethod
    def resolve_role(obj) -> Optional[str]:
        # Vérifier si current_user_membership existe et n'est pas vide
        if not hasattr(obj, 'current_user_membership') or not obj.current_user_membership:
            return None
            
        # current_user_membership est une liste, prendre le premier élément
        user_membership = obj.current_user_membership[0]
        
        # Vérifier si l'utilisateur est le propriétaire
        if hasattr(obj, 'owner') and obj.owner and obj.owner.organization_user == user_membership:
            return MemberEnum.SUPER_ADMIN
        elif user_membership.is_admin:
            return MemberEnum.ADMIN
        return MemberEnum.MEMBER

    class Meta:
        model = Organization
        exclude = {
            'id', 'users', 'deleted',
            'deleted_by_cascade', 'modified', 'created',
        }


class OrganizationCreateSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = {
            'name', 'description', 'email', 'slug',
            'location',
        }


class OrganizationDetailSchema(ModelSchema):
    class Meta:
        model = Organization
        exclude = ['users']


class OrganizationUserSchema(ModelSchema):
    user: UserSchema

    class Meta:
        model = OrganizationUser
        fields = '__all__'


class OrganizationUserUpdateSchema(ModelSchema):
    class Meta:
        model = OrganizationUser
        fields = ['id']
        fields_optional = ['role']
