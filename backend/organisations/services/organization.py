from uuid import UUID
from typing import Optional, List, Union
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db.models import Prefetch
from ninja.errors import ValidationError, AuthorizationError
from ninja_jwt.models import TokenUser
from organisations.models import (
    Organization,
    OrganizationUser,
)
from organisations.exceptions import OrganizationError
from organisations.caches import get_organization, get_organization_user
from organizations.backends import invitation_backend, registration_backend


UserModel = get_user_model()


class OrganizationService:

    @transaction.atomic
    def create_organization(self, user, name: str, **kwargs) -> Organization:
        """Create an organization and assign the user as owner."""

        organization = Organization.objects.create(name=name, **kwargs)

        org_user = OrganizationUser.objects.create(
            user=user,
            organization=organization,
            is_admin=True
        )

        owner_model = Organization.owner.related.related_model
        owner_model.objects.create(
            organization=organization,
            organization_user=org_user
        )
        return organization
    

    def user_organizations(self, user_id: Union[str, UUID]) -> List[Organization]:
        """Return all organizations where the user is an active member."""

        return (
            Organization.objects
            .filter(
                organization_users__user__pk=user_id,
                organization_users__is_active=True
            )
            .select_related("owner__organization_user__user")
            .prefetch_related(
                Prefetch(
                    "organization_users",
                    queryset=OrganizationUser.objects.filter(user__pk=user_id)
                    .select_related("user"),
                    to_attr="current_user_membership",
                )
            )
            .distinct()
            .order_by("name")
        )


    def organization_users(self, organization) -> List[OrganizationUser]:
        """List all active users of the organization."""

        return (
            OrganizationUser.objects
            .filter(organization=organization, is_active=True)
            .select_related("user")
            .order_by("joined_at")
        )
    

    def clean_user_email(self, email, organization):
        """Ensure email is not already used inside the organization."""

        exists = OrganizationUser.objects.filter(
            organization=organization,
            user__email__iexact=email,
        ).exists()

        if exists:
            raise ValidationError(_("There is already an organization member with this email address!"))

        return email


    def add_organization_user(self, organization, email, is_admin, sender):
        """Add or invite a user to the organization."""

        self.clean_user_email(email, organization)

        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            user = invitation_backend().invite_by_email(
                "email",
                domain="oxiliere.com",
                organization=organization,
                sender=sender,
            )

        invitation_backend().send_notification(
            user,
            domain="oxiliere.com",
            organization=organization,
            sender=sender,
        )


    def remove_organization_user(self, organization: Organization, user) -> bool:
        """Soft-remove a user from the organization."""

        try:
            org_user = OrganizationUser.objects.get(
                organization=organization,
                user=user,
                is_active=True
            )
            org_user.delete()
            return True
        except OrganizationUser.DoesNotExist:
            return False


    def get_organization_user(self, organization, user) -> Optional[OrganizationUser]:
        """Return a membership object for a user inside an organization."""

        kwargs = {"is_active": True}

        if isinstance(organization, Organization):
            kwargs["organization"] = organization
        else:
            kwargs["organization__slug"] = organization

        if isinstance(user, (UserModel, TokenUser)):
            kwargs["user__pk"] = user.pk
        else:
            kwargs["user__pk"] = user

        return get_organization_user(**kwargs)

    
    def user_can_manage_organization(self, organization: Organization, user) -> bool:
        """Check if the user can manage the organization members."""

        org_user = self.get_organization_user(organization, user)
        # Owners can manage members too
        return org_user.is_admin if org_user else False or self.is_organization_owner(organization, user)


    def is_admin_user(self, organization: Organization, user) -> bool:
        """Check if the user has admin rights. Owners are treated as admins."""
        
        org_user = self.get_organization_user(organization, user)
        return (org_user.is_admin if org_user else False) or self.is_organization_owner(organization, user)


    def get_organization_by_slug(self, slug: str, **kwargs) -> Optional[Organization]:
        return get_organization(slug=slug, **kwargs)


    def get_organization_by_id(
        self, 
        org_id: Union[UUID, str], 
        **kwargs
    ) -> Optional[Organization]:
        return get_organization(pk=org_id, **kwargs)


    def update_organization(
        self, 
        organization: Organization, 
        **kwargs
    ) -> Organization:
        """Update allowed fields of an organization."""

        for field, value in kwargs.items():
            if hasattr(organization, field):
                setattr(organization, field, value)

        organization.save()
        return organization
    

    def delete_organization(self, organization: Organization) -> bool:
        organization.delete()
        return True
    

    def is_organization_owner(self, organization, user, raise_exception=False):
        is_owner = organization.owner.organization_user == user

        if not is_owner and raise_exception:
            raise AuthorizationError()

        return is_owner


    def active_organization(self, organization, user, is_active=True):
        """Activate or deactivate an organization."""

        self.is_organization_owner(organization, user, raise_exception=True)

        if organization.is_active and is_active:
            raise OrganizationError("L'organisation est déjà active")

        if not organization.is_active and not is_active:
            raise OrganizationError("L'organisation est déjà inactive")

        organization.is_active = is_active
        organization.save()
        return organization



    # --- Invitations & Registration ---

    def accept_invitation(self, user_id, token, password):
        invitation_backend().activate_view(user_id, token, password)

    def activate_registration(self, user_id, token, password):
        registration_backend().activate_view(user_id, token, password)

    def remind_invitation(self, user_id, organization, sender=None):
        user = self.get_organization_user(organization, user_id)
        invitation_backend().send_reminder(user, sender=sender)

    def remind_registration(self, user_id, organization, sender=None):
        user = self.get_organization_user(organization, user_id)
        registration_backend().send_reminder(user, sender=sender)
