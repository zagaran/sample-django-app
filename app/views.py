import json
import re

from common.mixins import PermissionRequiredMixin, RequestMixin
from common.permissions import PermissionType
from common.s3 import create_presigned_upload_url
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage.filesystem import FileSystemStorage
from django.db import transaction
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView

from app.constants import SAMPLE_OBJECT_PK_URL_KWARG
from app.forms import SampleObjectCreateForm, SampleObjectEditForm

# START_FEATURE direct_upload
from app.constants import ATTACHMENT_PK_URL_KWARG
from app.models import Attachment, SampleObject
from app.serializers import AttachmentSerializer
# END_FEATURE direct_upload


class DashboardView(PermissionRequiredMixin, TemplateView):
    permission_required = PermissionType.dashboard
    template_name = "app/dashboard.html"

    # START_FEATURE direct_upload
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['storage_backend'] = "s3" if settings.AWS_STORAGE_BUCKET_NAME else "local"
        context['attachments'] = json.dumps([
            AttachmentSerializer(attachment).data
            for attachment in Attachment.objects.filter(deleted_on=None)
        ])
        context['sample_objects'] = SampleObject.objects.prefetch_related('attachments')
        return context
    # END_FEATURE direct_upload


class SampleObjectCreateView(PermissionRequiredMixin, RequestMixin, CreateView):
    permission_required = PermissionType.dashboard
    template_name = "app/sample_object_form.html"
    form_class = SampleObjectCreateForm
    model = SampleObject
    success_url = reverse_lazy('dashboard')


class SampleObjectDetailView(PermissionRequiredMixin, DetailView):
    permission_required = PermissionType.dashboard
    template_name = "app/sample_object_detail.html"
    model = SampleObject
    pk_url_kwarg = SAMPLE_OBJECT_PK_URL_KWARG
    context_object_name = "sample_object"

    # START_FEATURE direct_upload
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['storage_backend'] = "s3" if settings.AWS_STORAGE_BUCKET_NAME else "local"
        context['attachments'] = json.dumps([
            AttachmentSerializer(attachment).data
            for attachment in self.get_object().attachments.filter(deleted_on=None)
        ])
        return context
    # END_FEATURE direct_upload


class SampleObjectEditView(PermissionRequiredMixin, RequestMixin, UpdateView):
    permission_required = PermissionType.dashboard
    template_name = "app/sample_object_form.html"
    form_class = SampleObjectEditForm
    model = SampleObject
    pk_url_kwarg = SAMPLE_OBJECT_PK_URL_KWARG
    context_object_name = "sample_object"

    def get_success_url(self):
        return reverse('sample-object', kwargs={
            SAMPLE_OBJECT_PK_URL_KWARG: self.get_object().id,
        })


# START_FEATURE direct_upload
class FileUploadStartView(PermissionRequiredMixin, View):
    permission_required = PermissionType.dashboard

    def link_objects(self, attachment: Attachment, request):
        for key, value in request.GET.items():

            # Expect a query parameter key in this form: '<link_type>__<object>'
            # The value should be a UUID primary key
            if re.match(r"(\w+)__(\w+)", key):
                link_type, obj_accessor = key.split("__")
                if link_type == "mtm":
                    if (accessor := getattr(attachment, obj_accessor)):
                        accessor.add(get_object_or_404(accessor.model, pk=value))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        attachment_name = request.POST['name']

        # Create `Attachment` instance
        attachment = Attachment.objects.create(
            user=request.user,
            name=attachment_name,
        )
        self.link_objects(attachment, request)

        # Generate S3 path for file
        storage_path = Attachment._meta.get_field('file').generate_filename(attachment, attachment_name)
        attachment.file = storage_path
        attachment.save()

        # Set the presigned upload and completion URLs on response paylod
        serialized_data = {}
        url_kwargs = {ATTACHMENT_PK_URL_KWARG: str(attachment.id)}
        if isinstance(default_storage, FileSystemStorage):
            serialized_data['upload_presigned_url'] = reverse("attachment_upload_stream", kwargs=url_kwargs)
            serialized_data['upload_complete_url'] = reverse("attachment_upload_complete", kwargs=url_kwargs)
        else:
            serialized_data['upload_presigned_url'] = create_presigned_upload_url(object_name=storage_path)
            serialized_data['upload_complete_url'] = reverse("attachment_upload_complete", kwargs=url_kwargs)

        return JsonResponse(serialized_data)


class FileUploadStreamView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = PermissionType.dashboard

    model = Attachment
    pk_url_kwarg = ATTACHMENT_PK_URL_KWARG

    def post(self, request, *args, **kwargs):
        instance = self.get_object()

        file = request.FILES.get('file')
        if not file:
            return HttpResponse(status=400)

        instance.update(file=file)

        return JsonResponse({
            "id": instance.id,
            "name": instance.name,
            "url": instance.file.url,
        })


class FileUploadCompleteView(FileUploadStreamView):
    permission_required = PermissionType.dashboard

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update(upload_completed_on=timezone.now())
        return JsonResponse(AttachmentSerializer(instance).data)


class FileDownloadView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = PermissionType.dashboard

    model = Attachment
    pk_url_kwarg = ATTACHMENT_PK_URL_KWARG

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return instance.download_file()


class FileOpenView(FileDownloadView):
    permission_required = PermissionType.dashboard

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return instance.view_file()


class FileDeleteView(FileUploadStreamView):
    permission_required = PermissionType.dashboard

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update(deleted_on=timezone.now())
        return HttpResponse(status=200)
# END_FEATURE direct_upload
