from django.conf import settings
from urllib.parse import urljoin


def get_absolute_url(url: str, request=None):
    if request:
        # Build absolute URL using request
        return request.build_absolute_uri(url)
    else:
        # Fallback: build URL using MEDIA_URL and domain
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return urljoin(base_url, url)


def request_is_bound(request):
    """
    Check if a request is bound (has data), similar to Django Form.is_bound.
    """
    
    if not request or not hasattr(request, 'method'):
        return False
    
    if hasattr(request, 'data'):
        return (
            request.data is not None or
            bool(getattr(request, 'FILES', {})) or
            request.method in ('POST', 'PUT', 'PATCH')
        )
    
    elif hasattr(request, 'POST'):
        return (
            len(getattr(request, 'POST', {})) > 0 or
            len(getattr(request, 'FILES', {})) > 0 or
            request.method in ('POST', 'PUT', 'PATCH')
        )
    
    return False


def get_request_data(request):
    """
    Extract data from request, similar to how Django Forms get their data.
    
    Args:
        request: Django HttpRequest or DRF Request object
        
    Returns:
        dict: Request data (empty dict if no data)
    """
    if not request:
        return {}
    
    # DRF Request
    if hasattr(request, 'data'):
        return request.data or {}
    
    # Django HttpRequest
    elif hasattr(request, 'POST'):
        return dict(request.POST) if request.POST else {}
    
    return {}
