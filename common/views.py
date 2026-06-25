from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse
# START_FEATURE crispy_forms
from django.views.generic.edit import FormView
from common.forms import SampleForm
# END_FEATURE crispy_forms
# START_FEATURE celery
from datetime import timedelta
from django.utils import timezone
# END_FEATURE celery

from django.core.files.storage import storages
from reports.reports import UsersReport, PermissionsReport


class IndexView(TemplateView):
    template_name = "common/index.html"


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
class DjangoReactView(TemplateView):
    # TODO: delete me; this is just a reference example
    template_name = 'common/sample_django_react.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hello_msg'] = 'Component'
        context['sample_props'] = {'msg': 'sample props'}
        return context
# END_FEATURE django_react


# START_FEATURE crispy_forms
class SampleFormView(FormView):
    # TODO: delete me; this is just a reference example
    form_class = SampleForm
# END_FEATURE crispy_forms


class SampleReportView(TemplateView):
    report_classes = [UsersReport, PermissionsReport]
    template_name = 'common/report_demo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reports = []
        for ReportClass in self.report_classes:
            prefix = ReportClass.report_folder
            report_file_paths = [f"{prefix}/{file_name}" for file_name in
                                 storages["reports"].listdir(prefix)[1]]
            reports.extend({
                               "name": prefix,
                               "generated_on": storages[
                                   "reports"].get_created_time(file),
                               "url": storages["reports"].url(file)
                           } for file in report_file_paths)
        context["reports"] = reports
        return context

    def post(self, request):
        for ReportClass in self.report_classes:
            ReportClass().write_report()
        return redirect("report_generation_demo")


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)
