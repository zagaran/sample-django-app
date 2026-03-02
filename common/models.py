import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings
import boto3

# START_FEATURE direct_upload
from django.shortcuts import reverse
from common.constants import ATTACHMENT_PK_URL_KWARG
from django.template.defaultfilters import filesizeformat
# END_FEATURE direct_upload

from common.helpers import get_attachment_extension, remove_attachment_extension
from common.managers import UserManager

# START_FEATURE sentry
from sentry_sdk import capture_message
# END_FEATURE sentry


class TimestampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def update(self, update_dict=None, **kwargs):
        """ Helper method to update objects """
        if not update_dict:
            update_dict = kwargs
        update_fields = {"updated_on"}
        for k, v in update_dict.items():
            setattr(self, k, v)
            update_fields.add(k)
        self.save(update_fields=update_fields)

    class Meta:
        abstract = True


# Create your models here.
class User(AbstractUser, TimestampedModel):
    email = models.EmailField(unique=True)
    # START_FEATURE django_social
    username = None  # disable the AbstractUser.username field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
    # END_FEATURE django_social


# START_FEATURE django_storages
# TODO: delete me; this is just a reference example
def get_upload_prefix(instance, filename):
    return "%s/%s/%s" % (
        "uploads",
        instance.user_id,
        filename,
    )


class UploadFile(TimestampedModel):

    class Meta:
        abstract = True

    user = models.ForeignKey(User, related_name="files", on_delete=models.PROTECT)
    name = models.CharField(max_length=512)
    file = models.FileField(max_length=1024, upload_to=get_upload_prefix)

    # START_FEATURE direct_upload
    upload_completed_on = models.DateTimeField(null=True)

    def download_file(self) -> FileResponse | HttpResponse:
        extension = get_attachment_extension(self.file.name)
        filename = f"{remove_attachment_extension(self.name)}.{extension}".replace('"', '')
        s3_filename = self.file.name

        try:

            # Download file directly from S3
            if not settings.LOCALHOST:
                s3 = boto3.client('s3')
                url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        "Bucket": str(os.environ.get('AWS_STORAGE_BUCKET_NAME')),
                        "Key": s3_filename,
                        "ResponseContentDisposition": f'attachment; filename="{filename}"',
                    },
                    ExpiresIn=900
                )
                return HttpResponseRedirect(url)
            else:
                return FileResponse(self.file.open(), as_attachment=True, filename=filename)

        # START_FEATURE sentry
        except Exception:
            capture_message(f"Failed to download file ({self.id}) from S3 with path ({s3_filename})")
            raise Http404()
        # END_FEATURE sentry

    def view_file(self) -> FileResponse | HttpResponse:
        extension = get_attachment_extension(self.file.name)
        filename = f"{remove_attachment_extension(self.name)}.{extension}"

        # Get file directly from S3
        if not settings.LOCALHOST:
            return HttpResponseRedirect(self.file.url)
        else:
            return FileResponse(self.file.open(), as_attachment=False, filename=filename)

    # TODO: Should replace this with a DRF serializer
    def get_context_data(self):
        context = {
            "user": self.user.email,
            "name": self.name,
            "upload_completed_on": self.upload_completed_on,
            "view_url": reverse('attachment_open', kwargs={
                ATTACHMENT_PK_URL_KWARG: self.id,
            }),
            "download_url": reverse('attachment_download', kwargs={
                ATTACHMENT_PK_URL_KWARG: self.id,
            })
        }
        if self.file.storage.exists(self.file.name):
            context["size"] = filesizeformat(self.file.size)
            context["path"] = self.file.name
        return context
    # END_FEATURE direct_upload


# START_FEATURE direct_upload
class Attachment(UploadFile):
    pass

# END_FEATURE direct_upload
# END_FEATURE django_storages


# START_FEATURE user_action_tracking
class UserAction(TimestampedModel):
    user = models.ForeignKey(User, related_name="user_actions", on_delete=models.PROTECT)
    url = models.URLField(max_length=2083)
    method = models.CharField(max_length=64)
    url_name = models.CharField(max_length=256, null=True)
    status_code = models.IntegerField()
    user_agent = models.TextField(null=True)
# END_FEATURE user_action_tracking
