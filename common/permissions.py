from django.db.models import TextChoices


class UserOrganization(TextChoices):
    organization = ("organization", "Organization")


class UserRole(TextChoices):
    standard = ("standard", "Standard User")


class PermissionType(TextChoices):
    dashboard = ("dashboard", "View Dashboard")
    none = ("none", "No permission required")
