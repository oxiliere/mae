from datetime import datetime
from typing import Optional
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, QuerySet
from passport.enums import PassportStatus, BatchStatus
from passport.models import Passport, Batch


class PassportService:
    """
    Service class to handle Passport model operations.
    Provides methods for create, update, patch status, retrieve, delete,
    publish, and search/filter.
    """

    def create(self, **kwargs) -> Passport:
        """Create a new Passport with the given fields."""

        return Passport.objects.create(**kwargs)


    def update(self, passport_id: int, **kwargs) -> Passport:
        """Update an existing Passport by ID with the given fields."""

        passport = Passport.objects.get(id=passport_id)

        for key, value in kwargs.items():
            if value is not None:
                setattr(passport, key, value)

        passport.save()
        return passport


    def patch_status(self, passport_id: int, status: PassportStatus) -> Passport:
        """Update only the status field of a Passport."""
        
        passport = Passport.objects.get(id=passport_id)
        passport.status = status.value
        passport.save(update_fields=["status"])
        return passport
    

    def get(self, passport_id: int) -> Passport:
        """Retrieve a single Passport by its ID."""
        
        return Passport.objects.get(id=passport_id)


    def delete(self, passport_id: int) -> bool:
        """Delete a Passport by its ID."""

        passport = Passport.objects.get(id=passport_id)
        passport.delete()
        return True


    def publish(self, passport: Passport, published_at=None) -> Passport:
        """Publish a Passport and set its published_at timestamp."""
    
        passport.status = PassportStatus.PUBLISHED.value
        passport.published_at = published_at or timezone.now()
        passport.save(update_fields=["status", "published_at"])
        return passport
    

    def search_and_filter_passports(self, search=None, **kwargs) -> QuerySet[Passport]:
        """
        Search and filter passports.
        Supports text search on multiple fields and additional filtering via kwargs.
        """

        qs = Passport.objects.all()

        if search:
            qs = qs.filter(
                Q(code__icontains=search)
                | Q(coupon_id__icontains=search)
                | Q(first_name__icontains=search)
                | Q(middle_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(gender__icontains=search)
                | Q(status__icontains=search)
                # Datetime fields can't be icontains safely → convert search to date
                | Q(published_at__date=search) if self._is_date(search) else Q()
                | Q(batch__received_date__date=search) if self._is_date(search) else Q()
            )

        if kwargs:
            qs = qs.filter(**kwargs)

        return qs


    def _is_date(self, value: str) -> bool:
        """Internal safe-check to see if search is a date-like string."""
        try:
            datetime.fromisoformat(value)
            return True
        except Exception:
            return False



class BatchService:
    """
    Service class to handle Batch model operations.
    Provides methods for create, update, delete, search/filter, and publish batches.
    """

    @transaction.atomic
    def create(
        self,
        organization: int,
        status: str = BatchStatus.PENDING.value,
        received_date: Optional[datetime] = None,
    ) -> Batch:
        """
        Create a new Batch with an optional received_date.
        Rolls back if assigning the organization fails.
        """
        
        batch = Batch.objects.create(
            received_date=received_date or timezone.now(),
            status=status,
        )
        batch.set_organization(organization)
        return batch


    @transaction.atomic
    def update(
        self, 
        batch_id: int,
        organization: int | None = None,
        status: BatchStatus | None = None,
        received_date: datetime | None = None
    ) -> Batch:
        """
        Update an existing Batch by ID.
        Rolls back all changes if assigning the organization fails.
        """

        batch = Batch.objects.get(id=batch_id)

        if organization is not None:
            batch.set_organization(organization)

        if received_date is not None:
            batch.received_date = received_date

        if status is not None:
            batch.status = status.value

        batch.save()
        return batch


    def delete(self, batch_id) -> bool:
        """Delete a Batch by ID. Prevents deletion if already published."""

        batch = Batch.objects.get(id=batch_id)
        if batch.status == BatchStatus.PUBLISHED.value:
            raise ValueError("Cannot delete a published batch. Archive it instead.")
        batch.delete()
        return True


    def search_and_filter_batches(self, search: str = None, **kwargs) -> QuerySet[Batch]:
        """Search and filter batches. Supports text search and dynamic filtering."""

        if search:
            qs = self._search(search)
        else:
            qs = Batch.objects.all()

        if kwargs:
            qs = qs.filter(**kwargs)

        return qs
    

    def _search(self, search: str = None) -> QuerySet[Batch]:
        """Internal helper for textual search on Batch fields."""

        return Batch.objects.filter(
            Q(status__icontains=search)
            | (
                Q(received_date__date=search)
                if self._is_date(search)
                else Q()
            )
        )

    def _is_date(self, value: str) -> bool:
        try:
            datetime.fromisoformat(value)
            return True
        except Exception:
            return False


    def publish(self, batch_id: int, all: bool = True) -> bool:
        """
        Publish passports within a batch.
        - If all=True, publish all passports in the batch.
        - Otherwise, only publish passports with status COMPLETED.
        Updates the batch status accordingly.
        """

        batch = self._get_valid_batch(batch_id)
        passports = self._get_batch_passports(batch)
        to_publish = self._determine_publish_scope(passports, all)

        if not to_publish.exists():
            return False

        updated_count = to_publish.update(status=PassportStatus.PUBLISHED.value)
        self._sync_batch_status(batch, passports)

        return updated_count > 0
    
    
    def get_passports(self, batch_id: int, **filters) -> QuerySet[Passport]:
        """
        Retourne tous les passeports d'un batch donné avec des filtres optionnels.
        """
        batch = Batch.objects.get(id=batch_id)
        passports = self._get_batch_passports(batch)
        if filters:
            passports = passports.filter(**filters)
        return passports


    def _get_batch_passports(self, batch: Batch) -> QuerySet[Passport]:
        """
        Return all passports belonging to the given batch.
        Raise ValueError If the batch contains no passports.
        """
        passports = Passport.objects.filter(batch=batch)

        if not passports.exists():
            raise ValueError("No passports found in this batch.")

        return passports


    def _determine_publish_scope(
        self, 
        passports: QuerySet[Passport], 
        all: bool
    ) -> QuerySet[Passport]:
        """
        Determine which passports should be published.
        Return a queryset that contains passports that match 
        the chosen publication scope.
        """
        if all:
            return passports
        return passports.filter(status=PassportStatus.COMPLETED.value)

