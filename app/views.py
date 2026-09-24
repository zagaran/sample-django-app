
from common.mixins import PermissionRequiredMixin, RequestFormMixin
from common.permissions import Permission
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from app.constants import SAMPLE_OBJECT_PK_URL_KWARG
from app.forms import SampleObjectCreateForm, SampleObjectEditForm
from app.models import SampleObject

# START_FEATURE direct_upload
from attachments_framework.models import Attachment
from attachments_framework.serializers import serialize_attachments
# END_FEATURE direct_upload


class DashboardView(PermissionRequiredMixin, TemplateView):
    permission_required = Permission.dashboard
    template_name = "app/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sample_objects'] = SampleObject.objects.all()
        # START_FEATURE direct_upload
        context['attachments'] = serialize_attachments(
            Attachment.objects.active().select_related('user'),
            request=self.request,
        )
        # END_FEATURE direct_upload
        return context


class SampleObjectCreateView(PermissionRequiredMixin, RequestFormMixin, CreateView):
    permission_required = Permission.dashboard
    template_name = "app/sample_object_form.html"
    form_class = SampleObjectCreateForm
    model = SampleObject
    success_url = reverse_lazy('dashboard')


class SampleObjectDetailView(PermissionRequiredMixin, DetailView):
    permission_required = Permission.dashboard
    template_name = "app/sample_object_detail.html"
    model = SampleObject
    pk_url_kwarg = SAMPLE_OBJECT_PK_URL_KWARG
    context_object_name = "sample_object"


class SampleObjectEditView(PermissionRequiredMixin, RequestFormMixin, UpdateView):
    permission_required = Permission.dashboard
    template_name = "app/sample_object_form.html"
    form_class = SampleObjectEditForm
    model = SampleObject
    pk_url_kwarg = SAMPLE_OBJECT_PK_URL_KWARG
    context_object_name = "sample_object"

    def get_success_url(self):
        return reverse('sample-object', kwargs={
            SAMPLE_OBJECT_PK_URL_KWARG: self.object.id,
        })
