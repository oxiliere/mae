from uuid import UUID
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db.models import Prefetch
from typing import Optional, List

from ninja.errors import ValidationError, AuthorizationError
from ninja_jwt.models import TokenUser
from organizations.backends import invitation_backend, registration_backend
from organisations.models import (
    Organization,
    OrganizationUser,
)
from organisations.exceptions import OrganizationError
from organisations.caches import get_organization, get_organization_user




UserModel = get_user_model()



class OrganizationService:
    
    @transaction.atomic
    def create_organization(self, user, name: str, **kwargs) -> Organization:
        """Create a new organization with the user as owner"""
        # Create organization
        organization = Organization.objects.create(
            name=name,
            **kwargs
        )
        
        # Create organization user with owner role
        new_user = OrganizationUser.objects.create(
            user=user,
            organization=organization,
            is_admin=True
        )

        org_owner_model = Organization.owner.related.related_model

        org_owner_model.objects.create(
            organization=organization, organization_user=new_user
        )
        return organization
    
    def user_organizations(self, user_id: str | UUID) -> List[Organization]:
        """Get all organizations for a user"""
        return Organization.objects.filter(
            organization_users__user__pk=user_id,
            organization_users__is_active=True
        ).select_related(
            'owner__organization_user__user'
        ).prefetch_related(
            Prefetch(
                'organization_users',
                queryset=OrganizationUser.objects.filter(
                    user__pk=user_id
                ).select_related('user'),
                to_attr='current_user_membership'
            )
        ).distinct().order_by('name')

    def organization_users(self, organization) -> List[OrganizationUser]:
        """Get all users in an organization"""
        return OrganizationUser.objects.filter(
            organization=organization,
            is_active=True
        ).select_related('user').order_by('joined_at')

    
    def clean_user_email(self, email, organization):
        # Check if user with this email is already in the organization
        if OrganizationUser.objects.filter(
            organization=organization,
            user__email__iexact=email,
        ).exists():
            raise ValidationError(
                _("There is already an organization member with this email address!")
            )
        return email

    def add_organization_user(self, organization, email, is_admin, sender):
        self.clean_user_email(email, organization)

        user = None
        try:
            user = get_user_model().objects.get(
                email__iexact=email
            )
        except get_user_model().DoesNotExist:
            user = invitation_backend().invite_by_email(
                "email",
                **{
                    "domain": "oxiliere.com",
                    "organization": organization,
                    "sender": sender,
                },
            )

        invitation_backend().send_notification(
            user,
            **{
                "domain": "oxiliere.com",
                "organization": organization,
                "sender": sender,
            },
        )
    
    def remove_organization_user(self, organization: Organization, user) -> bool:
        """Remove a user from organization"""
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
    
    def get_organization_user(self, organization: Organization | str, user) -> Optional[OrganizationUser]:
        """Get user in organization"""
        kwargs = {
            "is_active": True
        }
        
        if isinstance(organization, Organization):
            kwargs['organization'] = organization
        elif isinstance(organization, str):
            kwargs["organization__slug"] = organization
        else:
            raise ValueError("Organization must an instance of Organization or a string/UUID")

        if isinstance(user, (UserModel, TokenUser)):
            kwargs['user__pk'] = user.pk
        elif isinstance(user, (str, UUID,)):
            kwargs["user__pk"] = user
        else:
            raise ValueError("User must an instance of UserModel or a string/UUID, instance of ", type(user))
        
        return get_organization_user(**kwargs)
    
    def user_can_manage_organization(self, organization: Organization, user) -> bool:
        """Check if user can manage organization"""
        user = self.get_organization_user(organization, user)
        return user.is_admin
    
    def is_admin_user(self, organization: Organization, user) -> bool:
        """Check if user has specific permission in organization"""
        user = self.get_organization_user(organization, user)
        if not user: return False
        return user.is_admin
    
    def get_organization_by_slug(self, slug: str, **kwargs) -> Optional[Organization]:
        """Get organization by slug"""
        return get_organization(slug=slug, **kwargs)
    
    def get_organization_by_id(self, org_id: UUID | str, **kwargs) -> Optional[Organization]:
        """Get organization by ID"""
        return get_organization(pk=org_id, **kwargs)
    
    def update_organization(self, organization: Organization, **kwargs) -> Organization:
        """Update organization details"""
        for field, value in kwargs.items():
            if hasattr(organization, field):
                setattr(organization, field, value)
        
        organization.save()
        return organization
    
    
    def delete_organization(self, organization: Organization) -> bool:
        """Soft delete organization"""
        organization.delete()
        return True

    def is_organization_owner(self, organization, user, raise_exception=False):
        is_owner = organization.owner.organization_user == user

        if not is_owner and raise_exception:
            raise AuthorizationError()

        return is_owner

    def active_organization(self, organization, user, is_active=True):
        self.is_organization_owner(organization, user, raise_exception=True)

        if not organization.is_active and not is_active:
            raise OrganizationError("L'organization est inactive")

        if organization.is_active and is_active:
            raise OrganizationError("L'organization est active")
        
        organization.is_active = False
        organization.save()
        return organization

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
