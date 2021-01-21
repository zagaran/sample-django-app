from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.contrib.auth import logout
# START_FEATURE crispy_forms
from django.views.generic.edit import FormView
from crispy_forms.tests.forms import SampleForm
# END_FEATURE crispy_forms


class IndexView(TemplateView):
    template_name = "common/index.html"


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("index")


# START_FEATURE crispy_forms
class SampleFormView(FormView):
    # TODO: delete me; this is just a reference example
    form_class = SampleForm
# END_FEATURE crispy_forms
