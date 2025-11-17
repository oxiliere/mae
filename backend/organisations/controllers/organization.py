from django.http import HttpRequest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from injector import inject
from ninja_extra import (
    api_controller, 
    http_get, 
    http_post, 
    http_put, 
    http_delete
)
from ninja_extra.permissions import IsAuthenticated
from ninja_extra.pagination import (
    paginate, 
    PageNumberPaginationExtra, 
    PaginatedResponseSchema
)
from organisations.services import OrganizationService
from organisations.models import Organization
from organisations.schemas import (
    OrganizationSchema,
    OrganizationCreateSchema,
    OrganizationDetailSchema,
    OrganizationUserSchema,
    AddUserSchema,
)
from utils_mixins.schemas import MessageSchema
from organisations.permissions import (
    IsOrganizationOwner,
    IsOrganizationMember,
    IsOrganizationAdmin,
)
from organisations.exceptions import (
    OrganizationError, 
    OrganizationAccessError
)
from django.db.models import Q



User = get_user_model()


@api_controller(
    "/organizations",
    tags=["Organizations"],
    permissions=[IsAuthenticated],
)
class OrganizationController:
    """
    Controller to manage organizations: CRUD operations 
    and activation/deactivation.
    """

    @inject
    def __init__(self, service: OrganizationService):
        """Inject the OrganizationService to handle business logic."""
        self.service = service


    @http_get(
        "", 
        response=PaginatedResponseSchema[OrganizationSchema]
    )
    @paginate(PageNumberPaginationExtra, page_size=20)
    def list(self, request: HttpRequest):
        """List all organizations where the authenticated user is a member."""
        return self.service.user_organizations(request.user.id)


    @http_post(
        "", 
        response={201: OrganizationDetailSchema, 400: MessageSchema}
    )
    def create(self, request: HttpRequest, data: OrganizationCreateSchema):
        """Create a new organization and assign the requesting user as owner."""

        try:
            org = self.service.create_organization(request.user, **data.dict())
            return 201, org
        except IntegrityError:
            return 400, MessageSchema(detail="Organization with this name already exists")


    @http_get(
        "/{slug}",
        response={200: OrganizationDetailSchema, 404: MessageSchema},
        permissions=[IsOrganizationMember()],
    )
    def retrieve(self, request, slug: str):
        """Retrieve details of a specific organization by its slug."""

        try:
            org = Organization.objects.get(slug=slug, is_active=True)
            if not self.service.get_organization_user(org, request.user):
                return 404, MessageSchema(detail="Organization not found")
            return 200, org
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")


    @http_put(
        "/{org_id}",
        response={200: OrganizationDetailSchema, 404: MessageSchema},
        permissions=[IsOrganizationOwner()],
    )
    def update(self, request, org_id: str, data):
        """Update an existing organization's details. Only owners can update."""
        try:
            org = Organization.objects.get(id=org_id, is_active=True)
            updated = self.service.update_organization(org, **data.dict(exclude_unset=True))
            return 200, updated
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")


    @http_delete(
        "/{org_id}",
        response={200: MessageSchema, 404: MessageSchema},
        permissions=[IsOrganizationOwner()],
    )
    def delete(self, request, org_id: str):
        """Delete an organization. Only owners can delete."""
        try:
            org = Organization.objects.get(id=org_id, is_active=True)
            self.service.delete_organization(org)
            return 200, MessageSchema(detail="Organization deleted successfully")
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")


    @http_post(
        "/{org_id}/activate",
        response={200: MessageSchema, 403: MessageSchema, 404: MessageSchema},
        permissions=[IsOrganizationOwner()],
    )
    def activate(self, request, org_id: str):
        """Activate an organization. Only owners can activate."""
        try:
            org = Organization.objects.get(id=org_id)
            self.service.active_organization(org, request.user, is_active=True)
            return 200, MessageSchema(detail="Organization activated")
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
        except (OrganizationError, OrganizationAccessError) as e:
            return 403, MessageSchema(detail=str(e))


    @http_post(
        "/{org_id}/deactivate",
        response={200: MessageSchema, 403: MessageSchema, 404: MessageSchema},
        permissions=[IsOrganizationOwner()],
    )
    def deactivate(self, request, org_id: str):
        """Deactivate an organization. Only owners can deactivate."""
        try:
            org = Organization.objects.get(id=org_id, is_active=True)
            self.service.active_organization(org, request.user, is_active=False)
            return 200, MessageSchema(detail="Organization deactivated")
        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")
        except (OrganizationError, OrganizationAccessError) as e:
            return 403, MessageSchema(detail=str(e))



@api_controller(
    "/organizations/{org_id}/users",
    tags=["Organization Users"],
    permissions=[IsAuthenticated],
)
class OrganizationUsersController:
    """Controller to manage users within an organization: list, add, remove."""

    @inject
    def __init__(self, service: OrganizationService):
        """Inject the OrganizationService to handle user-related business logic."""

        self.service = service


    @http_get(
        "",
        response=PaginatedResponseSchema[OrganizationUserSchema],
        permissions=[IsOrganizationMember()],
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list(self, request, org_id: str):
        """List all users in the organization."""

        try:
            org = Organization.objects.get(id=org_id, is_active=True)
            return self.service.organization_users(org)
        except Organization.DoesNotExist:
            return []


    @http_post(
        "",
        response={201: MessageSchema, 403: MessageSchema, 404: MessageSchema},
        permissions=[IsOrganizationAdmin()],
    )
    def add(self, request, org_id: str, data: AddUserSchema):
        """Add a new user to the organization. Only admins can add users."""

        try:
            org = Organization.objects.get(id=org_id, is_active=True)

            if not self.service.is_admin_user(org, request.user):
                return 403, MessageSchema(detail="Permission denied")

            self.service.add_organization_user(
                organization=org,
                email=data.email,
                is_admin=data.is_admin,
                sender=request.user,
            )
            return 201, MessageSchema(detail="User added successfully")

        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")


    @http_delete(
        "/{user_id}",
        response={200: MessageSchema, 403: MessageSchema, 404: MessageSchema},
        permissions=[IsOrganizationAdmin()],
    )
    def remove(self, request, org_id: str, user_id):
        """Remove a user from the organization. Only admins can remove users."""

        try:
            org = Organization.objects.get(id=org_id, is_active=True)

            if not self.service.user_can_manage_organization(org, request.user):
                return 403, MessageSchema(detail="Permission denied")

            target_user = User.objects.get(pk=user_id)

            if self.service.is_organization_owner(org, target_user):
                return 403, MessageSchema(detail="Cannot remove organization owner")

            removed = self.service.remove_organization_user(org, target_user)

            if removed:
                return 200, MessageSchema(detail="User removed successfully")
            return 404, MessageSchema(detail="User not found")

        except Organization.DoesNotExist:
            return 404, MessageSchema(detail="Organization not found")



    @http_get(
        "/search",
        response=PaginatedResponseSchema[OrganizationUserSchema],
        permissions=[IsOrganizationMember()],
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def search(self, request, org_id: str, query: str = ""):
        """Search users in an organization by name or email."""

        try:
            org = Organization.objects.get(id=org_id, is_active=True)

            users_qs = self.service.organization_users(org)

            if query:
                # Filter users by username or email containing the query string
                users_qs = users_qs.filter(
                    Q(user__username__icontains=query) |
                    Q(user__email__icontains=query)
                )

            return users_qs

        except Organization.DoesNotExist:
            return []
