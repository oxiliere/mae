from django.db import IntegrityError
from django.http import HttpRequest
from ninja import Schema
from ninja.errors import HttpError
from ninja_extra import (
    ControllerBase,
    api_controller, http_delete, 
    http_get, http_post, http_put
)
from ninja_extra.pagination import (
    paginate, PageNumberPaginationExtra, PaginatedResponseSchema
)
from ninja_extra.permissions import IsAuthenticated
from injector import inject
from uuid import UUID
from typing import Optional

from organisations.schemas import (
    OrganizationSchema,
    OrganizationCreateSchema,
    OrganizationDetailSchema,
    OrganizationUserSchema,
    PasswordSchema,
)
from organisations.services import OrganizationService
from organisations.exceptions import OrganizationError, OrganizationAccessError
from organisations.models import Organization
from organisations.permissions import (
    IsOrganizationOwner,
    IsOrganizationAdmin,
    IsOrganizationMember,
    isTargetUser,
)
from utils_mixins.schemas import MessageSchema
#from jwt_allauth.utils import load_user


class AddUserSchema(Schema):
    email: str
    is_admin: Optional[bool] = True



@api_controller("/organizations", tags=['Organizations'], permissions=[
    IsAuthenticated
])
class OrganizationController(ControllerBase):
    @inject
    def __init__(self, org_service: OrganizationService):
        self.org_service = org_service
    
    @http_get("", response=PaginatedResponseSchema[OrganizationSchema])
    @paginate(PageNumberPaginationExtra, page_size=20)
    def list_organizations(self, request: HttpRequest):
        """List user's organizations"""
        print(request.user)
        return self.org_service.user_organizations(request.user.id)
    
    @http_post("", response={201: OrganizationDetailSchema, 400: MessageSchema})
    #@load_user
    def create_organization(self, request: HttpRequest, data: OrganizationCreateSchema):
        """Create a new organization"""
        try:
            organization = self.org_service.create_organization(
                user=request.user,
                **data.dict()
            )
            return 201, organization
        except IntegrityError:
            return 400, MessageSchema(detail="Organization with this name already exists")
        except Exception as e:
            return 400, MessageSchema(detail=str(e))
    
    @http_get(
        "/{organization_id}", 
        response={200: OrganizationDetailSchema, 404: MessageSchema},
        permissions=[IsAuthenticated & IsOrganizationMember()]
    )
    def get_organization(self, request: HttpRequest, organization_id: str):
        """Get organization details"""
        try:
            organization = Organization.objects.get(slug=organization_id, is_active=True)
            # Check if user has access to this organization
            if not self.org_service.get_organization_user(organization, request.user):
                return 404, MessageSchema(detail="Organization not found")
            return 200, organization
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
    
    @http_get(
        "/check_id/{slug}", 
        response={200: MessageSchema, 404: MessageSchema},
        permissions=[IsAuthenticated]
    )
    def check_slug(self, request: HttpRequest, slug: str):
        """Check if organization slug (slug) is available"""
        try:
            # Check if organization with this slug exists
            organization = Organization.objects.filter(slug=slug, is_active=True).first()
            if organization:
                return 200, MessageSchema(detail="Slug is already taken")
            else:
                return 404, MessageSchema(detail="Slug is available")
        except Exception as e:
            return 404, MessageSchema(detail="Slug is available")


    @http_put(
        "/{organization_id}", 
        response={200: OrganizationDetailSchema, 404: MessageSchema, 403: MessageSchema},
        permissions=[IsAuthenticated & IsOrganizationOwner()]
    )
    def update_organization(self, request: HttpRequest, organization_id: str, data: OrganizationCreateSchema):
        """Update organization details"""
        try:
            organization = Organization.objects.get(id=organization_id, is_active=True)
            
            # Check if user can manage organization
            if not self.org_service.user_can_manage_organization(organization, request.user):
                return 403, MessageSchema(detail="Permission denied")
            
            updated_org = self.org_service.update_organization(organization, **data.dict(exclude_unset=True))
            return 200, updated_org
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
    
    @http_delete(
        "/{organization_id}", 
        response={200: MessageSchema, 404: MessageSchema, 403: MessageSchema},
        permissions=[IsAuthenticated & IsOrganizationOwner()]
    )
    def delete_organization(self, request: HttpRequest, organization_id: str):
        """Delete organization"""
        try:
            organization = Organization.objects.get(id=organization_id, is_active=True)
            
            # Check if user is owner
            if not self.org_service.is_organization_owner(organization, request.user):
                return 403, MessageSchema(detail="Only organization owner can delete organization")
            
            self.org_service.delete_organization(organization)
            return 200, MessageSchema(detail="Organization deleted successfully")
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
    
    # Organization Users Management
    @http_get(
        "/{organization_id}/users", 
        url_name="list_organization_users",
        response=PaginatedResponseSchema[OrganizationUserSchema],
        permissions=[IsAuthenticated & IsOrganizationMember()]
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_organization_users(self, request: HttpRequest, organization_id: str):
        """List organization users"""
        try:
            organization = Organization.objects.get(id=organization_id, is_active=True)
            
            # Check if user has access to this organization
            if not self.org_service.get_organization_user(organization, request.user):
                return []
            
            return self.org_service.organization_users(organization)
        except Organization.DoesNotExist:
            return []
    
    @http_post(
        "/{organization_id}/users", 
        url_name="add_organization_user",
        response={
            201: MessageSchema, 
            400: MessageSchema, 
            403: MessageSchema, 
            404: MessageSchema
        },
        permissions=[IsAuthenticated & IsOrganizationAdmin()]
    )
    def add_organization_user(self, request: HttpRequest, organization_id: str, data: AddUserSchema):
        """Add user to organization"""
        try:
            organization = Organization.objects.get(id=organization_id, is_active=True)
            
            # Check if user can invite users
            if not self.org_service.is_admin_user(organization, request.user):
                return 403, MessageSchema(detail="Permission denied")
            
            self.org_service.add_organization_user(
                organization=organization,
                email=data.email,
                is_admin=data.is_admin,
                sender=request.user
            )
            return 201, MessageSchema(detail="User added to organization successfully")
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
        # except Exception as e:
        #     return 400, MessageSchema(detail=str(e))
    
    @http_delete(
        "/{organization_id}/users/{user_id}", 
        response={200: MessageSchema, 404: MessageSchema, 403: MessageSchema},
        permissions=[IsAuthenticated & IsOrganizationAdmin()]
    )
    def remove_organization_user(self, request: HttpRequest, organization_id: str, user_id: UUID):
        """Remove user from organization"""
        try:
            organization = Organization.objects.get(id=organization_id, is_active=True)
            
            # Check if user can manage users
            if not self.org_service.user_can_manage_organization(organization, request.user):
                return 403, MessageSchema(detail="Permission denied")
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            target_user = User.objects.get(id=user_id)
            
            # Prevent removing organization owner
            if self.org_service.is_organization_owner(organization, target_user):
                return 403, MessageSchema(detail="Cannot remove organization owner")
            
            success = self.org_service.remove_organization_user(organization, target_user)
            if success:
                return 200, MessageSchema(detail="User removed from organization successfully")
            else:
                return 404, MessageSchema(detail="User not found in organization")
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
    

    @http_post(
        "/{organization_id}/activate", 
        response={
            200: MessageSchema, 
            404: MessageSchema, 
            403: MessageSchema
        },
        permissions=[IsAuthenticated & IsOrganizationOwner()]
    )
    def activate_organization(self, request: HttpRequest, organization_id: str):
        """Activate organization"""
        try:
            organization = Organization.objects.get(id=organization_id)
            
            self.org_service.active_organization(organization, request.user, is_active=True)
            return 200, MessageSchema(detail="Organization activated successfully")
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
        except (OrganizationError, OrganizationAccessError) as e:
            return 403, MessageSchema(detail=str(e))
    
    @http_post(
        "/{organization_id}/deactivate", 
        response={
            200: MessageSchema, 
            404: MessageSchema, 
            403: MessageSchema
        },
        permissions=[IsAuthenticated & IsOrganizationOwner()]
    )
    def deactivate_organization(self, request: HttpRequest, organization_id: str):
        """Deactivate organization"""
        try:
            organization = Organization.objects.get(id=organization_id, is_active=True)
            
            self.org_service.active_organization(organization, request.user, is_active=False)
            return 200, MessageSchema(detail="Organization deactivated successfully")
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
        except (OrganizationError, OrganizationAccessError) as e:
            return 403, MessageSchema(detail=str(e))

    @http_post(
        "/register/<uuid:user_id>/<str:token>",
        response={
            200: MessageSchema,
            403: MessageSchema
        },
        permissions=[IsAuthenticated & isTargetUser],
        url_name="user_register"
    )
    def user_register(self, request: HttpRequest, user_id: UUID, token: str, payload: PasswordSchema):
        if not payload.password == payload.password1:
            raise HttpError(
                status_code=400,
                message="Le mot de passe ne correspond pas"
            )
        try:
            self.org_service.activate_registration(user_id, token, payload.password)
            return 200, MessageSchema(detail="Registered successfully.")
        except (OrganizationError, OrganizationAccessError) as e:
            return 403, MessageSchema(detail=str(e))
