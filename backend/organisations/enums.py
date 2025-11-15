from enum import Enum


class InstallationStatus(str, Enum):
    FAILED = "failed"
    SUCCESS = "success"
    CANCELED = "canceled"
    RUNNING = "running"
    UN_INSTALLED = "un_installed"
    NOT_INSTALLED = "not_installed"


class TimeZoneEnum(str, Enum):
    KINSHASA = "Africa/Kinshasa"
    LUBUMBASHI = "Africa/Lubumbashi"
    DAKAR = "Africa/Dakar"
    NAIROBI = "Africa/Nairobi"



class MemberEnum(str, Enum):
    SUPER_ADMIN = "superadmin"
    ADMIN = "admin"
    MEMBER = "member"


class InvoiceStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class BillingTypeEnum(str, Enum):
    PER_USER = 'per_user'      # Facturation par utilisateur
    PER_QUOTA = 'per_quota'    # Facturation par quota (taille entreprise)


class PlanEnum(str, Enum):
    TRIAL = 'trial'
    FREE = 'free'
    INDIVIDUAL = 'individual'  # Freelances, consultants (facturation par utilisateur)
    MICRO = 'micro'        # 1-10 employés
    SMALL = 'small'        # 11-50 employés
    MEDIUM = 'medium'      # 51-250 employés
    LARGE = 'large'        # 251-1000 employés
    ENTERPRISE = 'enterprise'  # 1000+ employés
