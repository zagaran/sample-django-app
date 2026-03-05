from django.db.models import TextChoices


class UserOrganization(TextChoices):
    organization = ("organization", "Organization")


class UserRole(TextChoices):
    guest = ("guest", "Guest")
    standard = ("standard", "Standard")


class PermissionType(TextChoices):
    dashboard = ("dashboard", "View Dashboard")
    none = ("none", "No permission required")


ROLE_PERMISSIONS = {}
ROLE_PERMISSIONS[UserRole.guest] = []
ROLE_PERMISSIONS[UserRole.standard] = list(PermissionType)
