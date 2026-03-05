from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormMixin, UpdateView
from app.constants import SAMPLE_OBJECT_PK_URL_KWARG
from app.forms import SampleObjectCreateForm, SampleObjectEditForm
from app.models import Attachment, SampleObject
from django.conf import settings
from common.constants import ATTACHMENT_PK_URL_KWARG
from common.s3 import create_presigned_upload_url
from django.core.files.storage import default_storage
from django.core.files.storage.filesystem import FileSystemStorage
from django.db import transaction
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin


class DashboardView(TemplateView):
    template_name = "app/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['storage_backend'] = "s3" if settings.AWS_STORAGE_BUCKET_NAME else "local"
        context['attachments'] = [
            attachment.get_context_data()
            for attachment in self.request.user.files.all()
        ]
        context['sample_objects'] = SampleObject.objects.all()
        return context


class RequestFormMixin(FormMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class SampleObjectCreateView(RequestFormMixin, CreateView):
    template_name = "app/sample_object_form.html"
    form_class = SampleObjectCreateForm
    model = SampleObject
    success_url = reverse_lazy('dashboard')


class SampleObjectDetailView(DetailView):
    template_name = "app/sample_object_detail.html"
    model = SampleObject
    pk_url_kwarg = SAMPLE_OBJECT_PK_URL_KWARG
    context_object_name = "sample_object"


class SampleObjectEditView(RequestFormMixin, UpdateView):
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
# TODO: These views should have some permission structure
class FileUploadStartView(View):

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
        url_kwargs = {"attachment_id": str(attachment.id)}
        serialized_data = dict(request.POST)
        if isinstance(default_storage, FileSystemStorage):
            serialized_data['upload_presigned_url'] = reverse("attachment_upload_stream", kwargs=url_kwargs)
            serialized_data['upload_complete_url'] = reverse("attachment_upload_complete", kwargs=url_kwargs)
        else:
            serialized_data['upload_presigned_url'] = create_presigned_upload_url(object_name=storage_path)
            serialized_data['upload_complete_url'] = reverse("attachment_upload_complete", kwargs=url_kwargs)

        return JsonResponse(serialized_data)


class FileUploadStreamView(SingleObjectMixin, View):

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

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update(upload_completed_on=timezone.now())
        return JsonResponse(instance.get_context_data())


class FileDownloadView(SingleObjectMixin, View):

    model = Attachment
    pk_url_kwarg = ATTACHMENT_PK_URL_KWARG

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return instance.download_file()


class FileOpenView(FileDownloadView):

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return instance.view_file()
# END_FEATURE direct_upload
