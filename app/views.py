
from common.mixins import PermissionRequiredMixin, RequestFormMixin
from common.permissions import Permission
from common.s3 import create_presigned_upload_url
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
import json
from app.constants import ATTACHMENT_PK_URL_KWARG
from app.models import Attachment, SampleObject
from app.serializers import AttachmentSerializer
# END_FEATURE direct_upload


class DashboardView(PermissionRequiredMixin, TemplateView):
    permission_required = Permission.dashboard
    template_name = "app/dashboard.html"

    # START_FEATURE direct_upload
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachments'] = AttachmentSerializer(Attachment.objects.filter(deleted_on=None), many=True).data
        context['sample_objects'] = SampleObject.objects.prefetch_related('attachments')
        return context
    # END_FEATURE direct_upload


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

    # START_FEATURE direct_upload
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['attachments'] = AttachmentSerializer(obj.get_attachments(), many=True).data
        return context
    # END_FEATURE direct_upload


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


# START_FEATURE direct_upload
class FileUploadStartView(PermissionRequiredMixin, View):
    permission_required = Permission.dashboard

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        attachment_name = request.POST['name']

        # Create `Attachment` instance
        attachment = Attachment.objects.create(
            user=request.user,
            name=attachment_name,
        )

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


class FileUploadBaseView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = Permission.dashboard
    model = Attachment
    pk_url_kwarg = ATTACHMENT_PK_URL_KWARG


class FileUploadStreamView(FileUploadBaseView):

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


class FileUploadCompleteView(FileUploadBaseView):

    def _link_objects(self, attachment: Attachment):
        relations = json.loads(self.request.POST.get("relations", "{}"))
        for accessor_name, value in relations.items():
            accessor = getattr(attachment, accessor_name, None)
            if accessor is None:
                raise Exception(f'Accesor {accessor_name} does not exist on {attachment}')
            pks = value if isinstance(value, list) else [value]
            for pk in pks:
                accessor.add(get_object_or_404(accessor.model, pk=pk))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update(upload_completed_on=timezone.now())
        self._link_objects(instance)
        return JsonResponse(AttachmentSerializer(instance).data)


class FileDownloadView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = Permission.dashboard

    model = Attachment
    pk_url_kwarg = ATTACHMENT_PK_URL_KWARG

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return instance.download_file()


class FileOpenView(FileDownloadView):
    permission_required = Permission.dashboard

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return instance.view_file()


class FileDeleteView(FileUploadBaseView):

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update(deleted_on=timezone.now())
        return HttpResponse(status=200)
# END_FEATURE direct_upload
