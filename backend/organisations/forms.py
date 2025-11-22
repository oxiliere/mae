from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from organizations.models import OrganizationUser

from unfold.widgets import (
    UnfoldBooleanSwitchWidget,        # Pour les BooleanField (checkbox/switch)
    UnfoldAdminEmailInputWidget,      # Pour les EmailField
    UnfoldAdminTextInputWidget,       # Pour les CharField (texte, numéro)
    UnfoldAdminPasswordInput,         # Pour les PasswordInput
    UnfoldAdminSelectWidget,          # Pour les Select (ForeignKey)
)


User = get_user_model()


class OrganizationUserForm(forms.ModelForm):
    """
    Formulaire mis à jour avec les widgets Unfold pour le style.
    """

    # -----------------------------
    # User fields with Unfold Widgets
    # -----------------------------
    email = forms.EmailField(
        label=_('Adresse email'),
        widget=UnfoldAdminEmailInputWidget() # Unfold Email Widget
    )
    first_name = forms.CharField(
        label=_('Prénom'),
        max_length=150,
        required=True,
        widget=UnfoldAdminTextInputWidget() # Unfold Text Widget
    )
    last_name = forms.CharField(
        label=_('Nom'),
        max_length=150,
        required=True,
        widget=UnfoldAdminTextInputWidget() # Unfold Text Widget
    )
    phone_number = forms.CharField(
        label=_('Numéro de téléphone'),
        max_length=15,
        required=False,
        widget=UnfoldAdminTextInputWidget() # Unfold Text Widget
    )
    password = forms.CharField(
        label=_('Mot de passe (si nouvel utilisateur)'),
        widget=UnfoldAdminPasswordInput(), # Unfold Password Widget
        required=False
    )
    is_active = forms.BooleanField(
        label=_('Actif'),
        required=False,
        widget=UnfoldBooleanSwitchWidget() # Unfold Switch Widget
    )

    class Meta:
        model = OrganizationUser
        exclude = ('user',)
        fields = ['organization', 'is_admin']
        
        widgets = {
            'organization': UnfoldAdminSelectWidget(), # For FK 'organization'
            'is_admin': UnfoldBooleanSwitchWidget(),   # For boolean 'is_admin'
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Safely get the related user
        user_instance = getattr(self.instance, 'user', None)

        if user_instance:
            # Prefill User fields
            self.fields['email'].initial = user_instance.email
            self.fields['first_name'].initial = user_instance.first_name
            self.fields['last_name'].initial = user_instance.last_name
            self.fields['phone_number'].initial = getattr(user_instance, 'phone_number', '')
            self.fields['is_active'].initial = user_instance.is_active

            self.fields['password'].required = False
            self.fields['password'].label = _('Mot de passe (laisser vide pour ne pas changer)')


    # -----------------------------
    # Validation
    # -----------------------------
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_instance = getattr(self.instance, 'user', None)

        if not user_instance and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Un utilisateur avec cet email existe déjà."))
        return email


    def clean(self):
        cleaned_data = super().clean()
        user_instance = getattr(self.instance, 'user', None)

        if not user_instance and not cleaned_data.get('password'):
            self.add_error('password', _("Vous devez définir un mot de passe pour un nouvel utilisateur."))
        return cleaned_data


    # -----------------------------
    # Save method
    # -----------------------------
    def save(self, commit=True):
        org_user = super().save(commit=False)

        user_instance = getattr(org_user, 'user', None)

        if user_instance:
            user = user_instance
        else:
            user = User()
            user.username = self.cleaned_data['email']

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.is_active = self.cleaned_data.get('is_active', True)

        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            org_user.user = user            
            org_user.save()
            self.save_m2m()
        
        return org_user
    
