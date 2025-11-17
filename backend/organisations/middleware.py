from django.http import HttpRequest
from typing import Optional
from organisations.base import NullOrganization
from organisations.services import OrganizationService
from organisations.constants import (
    ORGANIZATION_HEADER_KEY, ORGANIZATION_QUERY_KEY
)




class CurrentOrganizationMiddleware:
    """
    Middleware pour définir l'organisation courante sur l'objet Request.
    Récupère l'ID de l'organisation depuis l'en-tête X-Organization-ID ou 
    depuis les kwargs de la requête et définit request.current_organization.
    Si aucune organisation n'est trouvée, utilise NullOrganization.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.org_service = OrganizationService()

    def __call__(self, request: HttpRequest):
        # Définir current_organization sur la requête
        
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.current_organization = self._get_current_organization(request)
        return None
    
    
    def _get_current_organization(self, request: HttpRequest):
        """
        Récupère l'organisation courante depuis les headers ou kwargs.
        Retourne NullOrganization si aucune organisation n'est trouvée.
        """
        org_id = self._extract_organization_id(request)
        if not org_id:
            return NullOrganization()
        
        try:
            
            org = self.org_service.get_organization_by_slug(org_id)
            if org:
                return org

        except (ValueError, TypeError, Exception) as e:
            pass
        
        return NullOrganization()
    
    def _extract_organization_id(self, request: HttpRequest) -> Optional[str]:
        """
        Extrait l'ID de l'organisation depuis les headers ou les kwargs.
        """
        
        # 1. Chercher dans les kwargs de la requête (pour les vues basées sur les classes)
        if hasattr(request, 'resolver_match') and request.resolver_match:
            kwargs = request.resolver_match.kwargs
            # Chercher différentes variantes possibles
            if ORGANIZATION_QUERY_KEY in kwargs:
                return kwargs[ORGANIZATION_QUERY_KEY]
        
        # 2. Chercher dans les paramètres GET
        org_id = request.GET.get(ORGANIZATION_QUERY_KEY)
        if org_id:
            return org_id

        # 3. Chercher dans les headers
        org_id = request.headers.get(ORGANIZATION_HEADER_KEY)
        if org_id:
            return org_id
        
        return None
