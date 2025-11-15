from django.core.exceptions import ImproperlyConfigured
from cacheops import cached_as, cached
from organisations.models import Organization, OrganizationUser



@cached_as(Organization, timeout=60*15)
def get_organization(**kwargs) -> Organization | None:
    try:
        return Organization.objects.get(**kwargs)
    except Organization.DoesNotExist:
        return None


@cached_as(OrganizationUser, timeout=60*15)
def get_organization_user(**kwargs) -> OrganizationUser | None:
    """
    Fonction cachée pour récupérer un OrganizationUser avec optimisations.
    """
    try:
        return OrganizationUser.objects.select_related(
            'organization',
            'organization__subscription_plan',
            'user'
        ).get(**kwargs)
    except OrganizationUser.DoesNotExist:
        return None


@cached(timeout=60*15)
def get_platform_admin_organization() -> Organization | None:
    org = Organization.objects.filter(is_platform_admin=True).order_by('created').first()
    
    if org is None:
        raise ImproperlyConfigured("Oups! The platform administrator must be created.")

    return org
