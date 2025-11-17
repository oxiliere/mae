from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
from auditlog.registry import auditlog
from utils_mixins.models import (
    UUIDPrimaryKeyMixin,
    ActiveMixin
)
from organizations.abstract import (
    AbstractOrganization,
    AbstractOrganizationUser,
    AbstractOrganizationOwner,
    AbstractOrganizationInvitation,
)
from organisations.enums import  TimeZoneEnum



class Organization(AbstractOrganization, SafeDeleteModel, UUIDPrimaryKeyMixin):
    """Core organization model"""
    _safedelete_policy = SOFT_DELETE_CASCADE

    # Organization details
    description = models.TextField(_('description'), blank=True, help_text=_('Description détaillée de l\'organisation'))
    email = models.EmailField(_('email'), blank=True, null=True, help_text=_('Email de contact principal'))
    phone = models.CharField(
        _('phone'), max_length=15,
        blank=True, null=True, 
        help_text=_('Téléphone contact principal')
    )

    # Location and contact
    location = models.CharField(
        _('localisation'), 
        max_length=100, 
        blank=True, 
        help_text=_('Ville ou région principale')
    )
    address = models.TextField(
        _('adresse'), 
        blank=True, 
        help_text=_('Adresse complète du siège social')
    )
    postal_code = models.CharField(
        _('code postal'), 
        max_length=10, 
        blank=True
    )
    country = models.CharField(
        _('pays'), 
        max_length=2, 
        default='CD', 
        help_text=_('Code pays ISO 2 lettres')
    )
    
    # Organization settings
    timezone = models.CharField(
        _('fuseau horaire'), 
        max_length=50, 
        default=TimeZoneEnum.LUBUMBASHI.value,
        choices=(
            (TimeZoneEnum.KINSHASA.value, _('Kinshasa (GMT + 1)')),
            (TimeZoneEnum.LUBUMBASHI.value, _('Lubumbashi (GMT + 2)')),
            (TimeZoneEnum.DAKAR.value, _('Dakar (GMT + 0)')),
            (TimeZoneEnum.NAIROBI.value, _('Nairobi (GMT + 3)')),
        )
    )
    

    class Meta:

        verbose_name = _('Organisation')
        verbose_name_plural = _('Organisations')
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]
    

    def clean(self):
        super().clean()
        if self.slug:
            # Check uniqueness of slug
            if Organization.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                raise ValidationError({'slug': _('Ce préfixe est déjà utilisé par une autre organisation')})
    

    def get_active_users_count(self):
        """Return the number of active users in this organization"""
        return self.organization_users.filter(is_active=True).count()
    

    def can_add_user(self):
        """Check if organization can add more users based on subscription"""
        plan_max_users = self.subscription_plan.max_users
        if plan_max_users is None:  # Unlimited users
            return True
        return self.get_active_users_count() < plan_max_users


    def is_admin(self, user):
        """
        Returns True is user is an admin in the organization, otherwise false
        """
        return (
            True if self.organization_users.filter(user__pk=user.pk, is_admin=True) else False
        )


    def is_owner(self, user):
        """
        Returns True is user is the organization's owner, otherwise false
        """
        return self.owner.organization_user.user.pk == user.pk


    def is_member(self, user):
        return self.users.all().filter(pk=user.pk).exists()


    def __str__(self):
        return f"{self.name} ({self.slug})"


    def save(self, keep_deleted=False, **kwargs):
        self.clean()
        if self.slug and not self.slug == self.slug:
            self.slug = self.slug
        return super().save(keep_deleted, **kwargs)



class OrganizationUser(AbstractOrganizationUser, SafeDeleteModel, UUIDPrimaryKeyMixin, ActiveMixin):
    """Links a user to the organization"""
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    # Status and dates
    joined_at = models.DateTimeField(_('date d\'adhésion'), auto_now_add=True)
    last_activity = models.DateTimeField(_('dernière activité'), auto_now=True)
    
    # Notifications preferences
    email_notifications = models.BooleanField(_('notifications email'), default=True)
    
    class Meta:
        verbose_name = _('Utilisateur d\'organisation')
        verbose_name_plural = _('Utilisateurs d\'organisation')
        unique_together = ['organization', 'user']
        indexes = [
            models.Index(fields=['joined_at']),
        ]
    
    
    def __str__(self):
        return f"{self.user} - {self.organization}"


class OrganizationOwner(AbstractOrganizationOwner):
    """Identifies ONE user, by AccountUser, to be the owner"""
    pass


class OrganizationInvitation(AbstractOrganizationInvitation, UUIDPrimaryKeyMixin):
    """Stores invitations for adding users to organizations"""
    pass


auditlog.register(Organization)
auditlog.register(OrganizationUser)
auditlog.register(OrganizationOwner)
auditlog.register(OrganizationInvitation)
