from ninja_extra.permissions import BasePermission
from organizations.models import Organization


class IsSameOrganizationMember(BasePermission):
    """
    Permission to ensure that the requesting user is a member of the 
    organization associated with the object (either directly or via a batch).
    
    - Object-level permission: checks `obj.organization` or `obj.batch.organization`.
    - Fails if the object has no associated organization.
    """
       
    message = "You do not belong to this organization"


    def has_permission(self, request, controller):
        return True  # check object-level instead
    

    def has_object_permission(self, request, controller, obj):
        organization = None

        if hasattr(obj, "organization"):
            organization = obj.organization
        elif hasattr(obj, "batch"):
            organization = obj.batch.organization

        if not organization:
            return False

        return organization.is_member(request.user)
