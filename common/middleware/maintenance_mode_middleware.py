from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http.response import HttpResponse
from django.template import loader


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

        # Disable middleware if MAINTENANCE_MODE is not on
        if not settings.MAINTENANCE_MODE:
            raise MiddlewareNotUsed()

    def __call__(self, request):
        # Render the template directly without the request to skip other steps
        content = loader.render_to_string("common/maintenance_mode.html")
        return HttpResponse(content)
