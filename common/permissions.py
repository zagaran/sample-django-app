from django.db.models import TextChoices

# START_FEATURE direct_upload
from attachments_framework.permissions import AttachmentPermission as BaseAttachmentPermission
# END_FEATURE direct_upload


class UserOrganization(TextChoices):
    organization = ("organization", "Organization")


class UserRole(TextChoices):
    guest = ("guest", "Guest")
    standard = ("standard", "Standard")


class Permission(TextChoices):
    dashboard = ("dashboard", "View Dashboard")


ROLE_PERMISSIONS = {}
ROLE_PERMISSIONS[UserRole.guest] = []
ROLE_PERMISSIONS[UserRole.standard] = list(Permission)


# START_FEATURE direct_upload
class AttachmentPermission(BaseAttachmentPermission):
    """ Attachment views require the same permission as the rest of the app """

    def has_permission(self, request, action):
        return super().has_permission(request, action) and request.user.has_permission(Permission.dashboard)
# END_FEATURE direct_upload
