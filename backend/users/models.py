from django.db import models

from django.contrib.auth.models import (
    AbstractUser, BaseUserManager,
    Group, Permission
)
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
from auditlog.registry import auditlog
from utils_mixins.models import (
    BaseModelMixin
)



class UserManager(BaseUserManager):
    """
    Gestionnaire personnalisé pour le modèle User
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Crée et sauvegarde un utilisateur avec l'email et le mot de passe donnés.
        """

        if not email:
            raise ValueError(_('L\'email est obligatoire'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crée et sauvegarde un superutilisateur avec l'email et le mot de passe donnés.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, SafeDeleteModel, BaseModelMixin):
    """
    Modèle d'utilisateur personnalisé qui utilise l'email comme identifiant unique
    et intègre la suppression sécurisée (soft delete)
    """
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    username = None
    role = models.PositiveSmallIntegerField(null=False, default=0)
    email = models.EmailField(
        _('adresse email'),
        unique=True,
        validators=[EmailValidator()]
    )
    
    phone_number = models.CharField(
        _('numéro de téléphone'), 
        max_length=15, blank=True, null=True,
    )

    language = models.CharField(
        _('langue'),
        max_length=10,
        default='fr',
        choices=[
            ('fr', 'Français'),
            ('en', 'English'),
        ]
    )

    groups = models.ManyToManyField(
        Group,
        related_name="custom_users",
        related_query_name="custom_user",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_users",
        related_query_name="custom_user",
        blank=True,
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-created_at']

    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """
        Retourne le prénom et le nom de l'utilisateur avec un espace entre les deux.
        """
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_short_name(self):
        """
        Retourne le prénom de l'utilisateur.
        """
        return self.first_name
    


# Enregistrement des modèles pour l'audit logging
auditlog.register(User)
