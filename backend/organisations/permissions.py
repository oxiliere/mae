from django.http import HttpRequest
from ninja_extra import permissions, ControllerBase
from .caches import get_organization
from .base import NullOrganization



class OrgBasePermission(permissions.BasePermission):

    def __init__(self, skip_id_check = False) -> None:
        self.skip_id_check = skip_id_check

    def get_organization(self, request: HttpRequest, controller):
        org = getattr(request, 'current_organization', NullOrganization())
        return org

    def has_permission(self, request: HttpRequest, controller: "ControllerBase") -> bool:
        organization = self.get_organization(request, controller)
        if not organization:
            return False
        
        return self.check_has_permission(organization, request, controller)

    def check_has_permission(self, organization, request, controller) -> bool:
        raise NotImplementedError()



class IsOrganizationOwner(OrgBasePermission):

    def check_has_permission(self, organization, request, controller):
        return organization.is_owner(request.user)


class IsOrganizationAdmin(OrgBasePermission):

    def check_has_permission(self, organization, request, controller):
        return organization.is_admin(request.user)
    

class IsOrganizationMember(OrgBasePermission):

    def check_has_permission(self, organization, request, controller):
        return organization.is_member(request.user)



class isTargetUser(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, controller: "ControllerBase") -> bool:
        user_id = controller.context.kwargs.get('user_id')
        return HttpRequest.user.pk == user_id


class isPlatformAdministrator(OrgBasePermission):
    def check_has_permission(self, organization, request, controller):
        return organization.is_platform_administrator() 
