# Organization base

class NullOrganization:
    """
    Classe représentant une organisation nulle/par défaut.
    Utilisée quand aucune organisation n'est trouvée dans la requête.
    """
    
    def __init__(self):
        self.id = None
        self.slug = None
        self.logo_url = None
        self.name = "Aucune organisation"
        self.is_active = False
        self.is_platform_admin = False
        self.organization_type = 'other'
    
    def __str__(self):
        return self.name
    
    def __bool__(self):
        return False
    
    def is_platform_administrator(self):
        return False
    
    def get_active_users_count(self):
        return 0
    
    def can_add_user(self):
        return False
