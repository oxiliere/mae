from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.utils.translation import gettext_lazy as _
from .models import OrganizationUser
from organizations import models as org_models
from django.contrib.auth.models import Group
from auditlog.models import LogEntry
from .forms import OrganizationUserForm


# All models of django-organizations and other models
ALL_ORG_MODELS = [
    org_models.Organization,
    org_models.OrganizationUser,
    org_models.OrganizationOwner,
    org_models.OrganizationInvitation,
    Group,
    LogEntry,
]


# Unregister unwanted models
for model in ALL_ORG_MODELS:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


@admin.register(OrganizationUser)
class OrganizationUserAdmin(UnfoldModelAdmin):
    form = OrganizationUserForm

    # List display with translated labels
    list_display = (
        "user_label",
        "organization_label",
        "is_admin_label",
        "is_active_label",
        "joined_at",
        "last_activity"
    )

    # Search fields on real model fields
    search_fields = [
        "organization__name", 
        "user__email"
    ]

    # Filters
    list_filter = ("is_admin", "is_active")

    # Date hierarchy
    date_hierarchy = "joined_at"


    # -----------------------------
    # Display methods with translation
    # -----------------------------
    def user_label(self, obj):
        """User label"""
        return obj.user
    user_label.short_description = _("Utilisateur")


    def organization_label(self, obj):
        """Organization label"""
        return obj.organization
    organization_label.short_description = _("Organisation")


    def is_admin_label(self, obj):
        """Admin label with Yes/No"""
        return _("Oui") if obj.is_admin else _("Non")
    is_admin_label.short_description = _("Administrateur")
    is_admin_label.admin_order_field = "is_admin"  # enable sorting


    def is_active_label(self, obj):
        """Active label with Yes/No"""
        return _("Oui") if obj.is_active else _("Non")
    is_active_label.short_description = _("Actif")
    is_active_label.admin_order_field = "is_active"  # enable sorting


    def save_model(self, request, obj, form, change):
        """
        Force l'utilisation de la méthode save() du formulaire personnalisé
        pour gérer la création/mise à jour du User et de l'OrganizationUser.
        """
        form.save()
