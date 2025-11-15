from datetime import datetime
from typing import Optional
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
            setattr(passport, key, value)
        passport.save()
        return passport


    def patch_status(self, passport_id: int, status: PassportStatus) -> Passport:
        """Update only the status field of a Passport."""
        
        passport = Passport.objects.get(id=passport_id)
        passport.status = status
        passport.save()
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
    
        passport.status = PassportStatus.PUBLISHED
        passport.published_at = published_at or timezone.now()
        passport.save()
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
                | Q(published_at__icontains=search)
                | Q(batch__received_date__icontains=search)
            )
        if kwargs:
            qs = qs.filter(**kwargs)
        return qs



class BatchService:
    """
    Service class to handle Batch model operations.
    Provides methods for create, update, delete, search/filter, and publish batches.
    """

    def create(self, received_date: datetime | None = None) -> Batch:
        """Create a new Batch with an optional received_date."""

        return Batch.objects.create(received_date=received_date)


    def update(self, batch_id, received_date: datetime | None = None) -> Batch:
        """Update an existing Batch's received_date by ID."""

        batch = Batch.objects.get(id=batch_id)
        if received_date:
            batch.received_date = received_date
            batch.save()
        return batch


    def delete(self, batch_id) -> bool:
        """Delete a Batch by ID. Prevents deletion if already published."""

        batch = Batch.objects.get(id=batch_id)
        if batch.status == BatchStatus.PUBLISHED:
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
            | Q(received_date__icontains=search)
        )


    def publish(self, batch_id: int, all: bool = True) -> bool:
        """
        Publish passports within a batch.
        - If all=True, publish all passports in the batch.
        - Otherwise, only publish passports with status COMPLETED.
        Updates the batch status accordingly.
        """

        batch = Batch.objects.get(id=batch_id)
        if batch.status == BatchStatus.PUBLISHED:
            raise ValueError("This batch is already published and cannot be republished.")

        passports = Passport.objects.filter(batch=batch)
        if not passports.exists():
            raise ValueError("No passports found in this batch.")

        to_publish = passports if all else passports.filter(status=PassportStatus.COMPLETED)
        if not to_publish.exists():
            return False

        updated_count = to_publish.update(status=PassportStatus.PUBLISHED)

        total = passports.count()
        published_count = passports.filter(status=PassportStatus.PUBLISHED).count()
        batch.status = BatchStatus.PUBLISHED if published_count == total and total > 0 else BatchStatus.PROCESSING
        batch.save()

        return updated_count > 0
