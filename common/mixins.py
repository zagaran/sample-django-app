from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.edit import FormMixin

from common.permissions import Permission


class PermissionRequiredMixin(AccessMixin):
    permission_required = None

    def dispatch(self, request, *args, **kwargs):
        if not self.permission_required:
            raise ImproperlyConfigured("Permission for view not specified.")
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Check that user has the required permission.
        if not request.user.has_permission(self.permission_required):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class RequestFormMixin(FormMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
