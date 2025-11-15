from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from organizations.backends.defaults import (
    InvitationBackend as OInvitationBackend,
    RegistrationBackend as ORegistrationBackend
)
from organisations.utils import is_strong_password
from organisations.exceptions import WeakPasswordError




class OBackendMinxin:
    def activate_view(self, user_id, token, password):
        """
        View function that activates the given User by setting `is_active` to
        true if the provided information is verified.
        """
        if not is_strong_password(password):
            raise WeakPasswordError(_("Le mot de passe est trop faible."))
            
        try:
            user = self.user_model.objects.get(id=user_id, is_active=False)
        except self.user_model.DoesNotExist:
            raise Http404(_("Your URL may have expired."))

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise Http404(_("Your URL may have expired."))
        
        user.set_password(password)
        user.save()
        self.activate_organizations(user)


class RegistrationBackend(OBackendMinxin, ORegistrationBackend):
    pass


class InvitationBackend(OBackendMinxin, OInvitationBackend):
    pass
