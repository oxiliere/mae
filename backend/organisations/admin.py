from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.contrib import admin
from .models import OrganizationUser
from django.contrib import admin
# We unregistrate all models we don't want
from organizations import models as org_models
from django.contrib.auth.models import Group
from auditlog.models import LogEntry


# All models of django-organizations and other models
ALL_ORG_MODELS = [
    org_models.Organization,
    org_models.OrganizationUser,
    org_models.OrganizationOwner,
    org_models.OrganizationInvitation,
    Group,
    LogEntry,
]


#Unregistre all the django-organizations models we don't want
for model in ALL_ORG_MODELS:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


# --- Organization ---

@admin.register(OrganizationUser)
class OrganizationUserAdmin(UnfoldModelAdmin):
    list_display = (
        "user", 
        "organization", 
        "is_admin", 
        "is_active", 
        "joined_at", 
        "last_activity"
    )
    search_fields = ("user__username", "organization__name")
    list_filter = ("is_admin", "is_active")
    date_hierarchy = "joined_at"

