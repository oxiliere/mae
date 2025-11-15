from enum import Enum


class PassportStatus(str, Enum):

    PUBLISHED = "published"   # The passport is ready and available for distribution
    DRAFT = "draft"           # The passport is being created or modified
    LOST = "lost"             # The passport has been reported lost
    TAKEN = "taken"           # The passport has been taken
    COMPLETED = "completed"   # The passport is ready to be published


class BatchStatus(str, Enum):

    PENDING = "pending"         # We are awaiting the receipt of some passports
    RECEIVED = "received"       # All passports have been received
    PROCESSING = "processing"   # Passports are being processed (data entry, sorting, etc.)
    COMPLETED = "completed"     # All passports have been processed and are ready for distribution
    PUBLISHED = "published"     # Publish the passports that are completed

