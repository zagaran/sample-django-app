from django.conf import ImproperlyConfigured
from django.contrib.auth.mixins import AccessMixin

from common.permissions import PermissionType


class PermissionRequiredMixin(AccessMixin):
    permission_required = None

    def dispatch(self, request, *args, **kwargs):
        if not self.permission_required:
            raise ImproperlyConfigured("Permission for view not specified.")
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Check that user has the required permission.
        if (
            not request.user.has_permission(self.permission_required)
            and self.permission_required != PermissionType.none
        ):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
