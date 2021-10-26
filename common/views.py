from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
# START_FEATURE crispy_forms
from django.views.generic.edit import FormView

from crispy_forms.tests.forms import SampleForm
# END_FEATURE crispy_forms


class IndexView(TemplateView):
    template_name = "common/index.html"


def HealthCheckView(View):
    def get():
        return HttpResponse("ok")


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("index")


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
