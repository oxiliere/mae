from django.utils import timezone
from django.utils.formats import date_format
from django.db import models
from passport.enums import (
    PassportStatus, 
    BatchStatus,
    GenderStatus,
)
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from organisations.models.organisations import Organization
from auditlog.registry import auditlog
from utils_mixins.models import (
    UUIDPrimaryKeyMixin, 
    TimestampMixin,
)




class Batch(SafeDeleteModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Represents a batch of passports.

    Attributes:
        received_date: The date this batch was received.
        status: Current status of the batch (Pending, Received, Processing, 
        Completed, Published).
        organization: Organization this batch belongs to.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    received_date = models.DateField(
        help_text=_("Date of the batch"),
        default=timezone.now,
        verbose_name=_("Date de réception"),
    )
    status = models.CharField(
        max_length=50,
        default=BatchStatus.PENDING.value,
        choices=(
            (BatchStatus.PENDING.value, _('En attente')),
            (BatchStatus.RECEIVED.value, _('Reçu')),
            (BatchStatus.PROCESSING.value, _('En traitement')),
            (BatchStatus.COMPLETED.value, _('Terminé')),
            (BatchStatus.PUBLISHED.value, _('Publié')),
        ),
        verbose_name="Statut",
        help_text=_("Status of the batch"),
    )
    organization = models.ForeignKey(
        Organization,
        null=True,
        on_delete=models.CASCADE,
        related_name="batches",
        help_text=_("The organization this batch belongs to"),
        verbose_name=_("Organization")
    )


    class Meta:
        
        verbose_name = _("Lot des passports")
        verbose_name_plural = _("Lots des passports")


    def set_organization(self, organization_id: int):
        """
        Assigns an organization to this batch by its ID.

        Args:
            organization_id (int): ID of the organization to assign.

        Raises:
            Organization.DoesNotExist: If no organization with the given ID exists.
        """
        try:
    
            organization = Organization.objects.get(id=organization_id)
            self.organization = organization
            self.save(update_fields=["organization"])

        except Organization.DoesNotExist:
        
            raise Organization.DoesNotExist(
                f"Organization with ID {organization_id} does not exist."
            )

            
    def __str__(self):
        local_date = date_format(self.received_date, format="DATE_FORMAT", use_l10n=True)
        status_label = self.get_status_display()

        return f"{local_date} – {status_label}"


class Passport(SafeDeleteModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Represents a passport within a batch.

    Attributes:
        batch: ForeignKey linking this passport to a Batch.
        code: Unique passport code.
        coupon_id: Unique coupon identifier.
        first_name: Holder's first name.
        middle_name: Holder's middle name (optional).
        last_name: Holder's last name.
        gender: Holder's gender.
        status: Current status of the passport (Draft, Published, Completed, Lost, Taken).
        published_at: DateTime when the passport was published.
        taken_at: DateTime when the passport was taken.
    """

    _safedelete_policy = 1

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="passports",
        verbose_name=_("Lot"),
        help_text=_("The batch this passport belongs to"),
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_("Code du passport"),
        help_text=_("Unique code for the passport"),
    )
    coupon_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_("ID du coupon"),
        help_text=_("Coupon identifier associated with the passport"),
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("Nom"),
        help_text=_("Last name of the passport holder"),
    )    
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Postnom"),
        help_text=_("Middle name of the passport holder"),
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("Prénom"),
        help_text=_("First name of the passport holder"),
    )
    gender = models.CharField(
        max_length=10,
        verbose_name=_("Genre"),
        choices=(
            (GenderStatus.MALE.value, _("Homme")),
            (GenderStatus.FEMALE.value, _("Femme")),
        ),  
        help_text=_("Gender of the passport holder"),
    )
    status = models.CharField(
        max_length=50,
        verbose_name=_("Statut"),
        help_text=_("Status of the passport"),
        default=PassportStatus.DRAFT.value,
        choices=(
            (PassportStatus.PUBLISHED.value, _('Publié')),
            (PassportStatus.DRAFT.value, _('Brouillon')),
            (PassportStatus.COMPLETED.value, _('Terminé')),
            (PassportStatus.LOST.value, _('Perdu')),
            (PassportStatus.TAKEN.value, _('Retiré')),
        )
    )
    published_at = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date de publication"),
        help_text=_("Publication date of the passport"),
    )
    taken_at = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date de retrait"),
        help_text=_("Date when the passport was taken"),
    )


    class Meta:
        
        verbose_name = _('Passport')
        verbose_name_plural = _('Passports')


    def __str__(self):
        return f"Passport {self.code} for {self.first_name} {self.last_name} (Batch: {self.batch.received_date})"


auditlog.register(Batch)
auditlog.register(Passport)

