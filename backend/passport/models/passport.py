from utils_mixins.models import BaseModelMixin
from django.utils import timezone
from django.db import models
from passport.enums import PassportStatus, BatchStatus
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from organisations.models.organisations import Organization



class Batch(SafeDeleteModel, BaseModelMixin):
    """
    Represents a batch of passports.

    Attributes:
        received_date: The date this batch was received.
        status: Current status of the batch (Pending, Received, Processing, Completed, Published).
        organization: Organization this batch belongs to.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    received_date = models.DateField(
        help_text="Date of the batch",
        default=timezone.now
    )
    status = models.CharField(
        max_length=50,
        help_text="Status of the batch",
        default=BatchStatus.PENDING.value,
        choices=(
            (BatchStatus.PENDING.value, _('Pending')),
            (BatchStatus.RECEIVED.value, _('Received')),
            (BatchStatus.PROCESSING.value, _('Processing')),
            (BatchStatus.COMPLETED.value, _('Completed')),
            (BatchStatus.PUBLISHED.value, _('Published')),
        )
    )
    organization = models.ForeignKey(
        Organization,
        null=True,
        on_delete=models.CASCADE,
        related_name="batches",
        help_text="The organization this batch belongs to",
    )


    def __str__(self):
        """
        String representation of a batch.
        """
        return f"Batch: {self.received_date} - {self.status}"


class Passport(SafeDeleteModel, BaseModelMixin):
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

    _safedelete_policy = SOFT_DELETE_CASCADE

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="passports",
        help_text="The batch this passport belongs to",
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique code for the passport",
    )
    coupon_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Coupon identifier associated with the passport",
    )
    first_name = models.CharField(
        max_length=100,
        help_text="First name of the passport holder",
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Middle name of the passport holder",
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Last name of the passport holder",
    )
    gender = models.CharField(
        max_length=10,
        help_text="Gender of the passport holder",
    )
    status = models.CharField(
        max_length=50,
        help_text="Status of the passport",
        default=PassportStatus.DRAFT.value,
        choices=(
            (PassportStatus.PUBLISHED.value, _('Published')),
            (PassportStatus.DRAFT.value, _('Draft')),
            (PassportStatus.COMPLETED.value, _('Completed')),
            (PassportStatus.LOST.value, _('Lost')),
            (PassportStatus.TAKEN.value, _('Taken')),
        )
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Publication date of the passport",
    )
    taken_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date when the passport was taken",
    )


    def __str__(self):
        """
        String representation of a passport.
        """
        return f"Passport {self.code} for {self.first_name} \
                 {self.last_name} (Batch: {self.batch.received_date})"
