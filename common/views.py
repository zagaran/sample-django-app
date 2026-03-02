from django.contrib.auth import logout
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render, reverse
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse

# START_FEATURE crispy_forms
from django.views.generic.edit import FormView
from common.constants import ATTACHMENT_PK_URL_KWARG
from common.forms import SampleForm
from common.models import Attachment
# END_FEATURE crispy_forms

# START_FEATURE direct_upload
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.storage.filesystem import FileSystemStorage
from django.views.generic.detail import SingleObjectMixin
from common.s3 import create_presigned_upload_url
# END_FEATURE direct_upload


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
        return HttpResponse(status=200)
# END_FEATURE direct_upload


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)
