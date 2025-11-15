from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
)
from ninja.security import (
    HttpBasicAuth,
)


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = django_authenticate(email=username, password=password)
        if user and user.is_active:
            django_login(request, user)
            return user
        return None


basic_auth = BasicAuth()

