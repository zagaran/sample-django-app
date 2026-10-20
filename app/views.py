from functools import cached_property

from common.mixins import PermissionRequiredMixin, RequestFormMixin
from common.permissions import Permission
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from app.constants import SAMPLE_OBJECT_PK_URL_KWARG, SAMPLE_SUB_OBJECT_PK_URL_KWARG
from app.forms import SampleObjectCreateForm, SampleObjectEditForm, SampleSubObjectCreateForm, SampleSubObjectEditForm
from app.models import SampleObject, SampleSubObject

# START_FEATURE direct_upload
from attachments_framework.models import Attachment
from attachments_framework.serializers import serialize_attachments
# END_FEATURE direct_upload


def get_sub_objects():
    return SampleSubObject.objects.select_related(
        'created_by',
        # START_FEATURE direct_upload
        'attachment',
        # END_FEATURE direct_upload
    )


class DashboardView(PermissionRequiredMixin, TemplateView):
    permission_required = Permission.dashboard
    template_name = "app/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sample_objects'] = SampleObject.objects.prefetch_related(
            Prefetch('sub_objects', queryset=get_sub_objects())
        )
        # START_FEATURE direct_upload
        # Includes sub object attachments, since they are attachments like any other
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_objects'] = get_sub_objects().filter(sample_object=self.object)
        return context


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


class SampleSubObjectMixin(PermissionRequiredMixin):
    """ Scopes a view to the sub objects of the sample object in the URL """
    permission_required = Permission.dashboard
    model = SampleSubObject
    pk_url_kwarg = SAMPLE_SUB_OBJECT_PK_URL_KWARG
    context_object_name = "sample_sub_object"

    @cached_property
    def sample_object(self) -> SampleObject:
        return get_object_or_404(SampleObject, pk=self.kwargs[SAMPLE_OBJECT_PK_URL_KWARG])

    def get_queryset(self):
        return SampleSubObject.objects.filter(sample_object=self.sample_object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sample_object'] = self.sample_object
        return context

    def get_success_url(self):
        return reverse('sample-object', kwargs={
            SAMPLE_OBJECT_PK_URL_KWARG: self.sample_object.id,
        })


class SampleSubObjectFormMixin(SampleSubObjectMixin, RequestFormMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['sample_object'] = self.sample_object
        return kwargs


class SampleSubObjectCreateView(SampleSubObjectFormMixin, CreateView):
    template_name = "app/sample_object_form.html"
    form_class = SampleSubObjectCreateForm


class SampleSubObjectEditView(SampleSubObjectFormMixin, UpdateView):
    template_name = "app/sample_object_form.html"
    form_class = SampleSubObjectEditForm


class SampleSubObjectDeleteView(SampleSubObjectMixin, DeleteView):
    template_name = "app/sample_sub_object_confirm_delete.html"
