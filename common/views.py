from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse

from common.mixins import PermissionRequiredMixin
from common.permissions import PermissionType

# START_FEATURE crispy_forms
from django.views.generic.edit import FormView
from common.forms import SampleForm
# END_FEATURE crispy_forms
# START_FEATURE celery
from datetime import timedelta
from django.utils import timezone
# END_FEATURE celery


class IndexView(TemplateView):
    template_name = "common/index.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().get(request, *args, **kwargs)


class LogoutView(View):

    def post(self, request):
        logout(request)
        return redirect("index")


class RobotsTxtView(View):

    def get(self, request):
        if settings.PRODUCTION:
            # Allow all (note that a blank Disallow block means "allow all")
            lines = ["User-agent: *", "Disallow:"]
        else:
            # Block all
            lines = ["User-agent: *", "Disallow: /"]
        return HttpResponse("\n".join(lines), content_type="text/plain")


# START_FEATURE django_react
class DjangoReactView(PermissionRequiredMixin, TemplateView):
    # TODO: delete me; this is just a reference example
    permission_required = PermissionType.dashboard
    template_name = 'common/sample_django_react.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hello_msg'] = 'Component'
        context['sample_props'] = {'msg': 'sample props'}
        return context
# END_FEATURE django_react


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
