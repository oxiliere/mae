

class OrganizationError(Exception):
    pass


class OrganizationAccessError(OrganizationError):
    pass


class WeakPasswordError(OrganizationError):
    pass

