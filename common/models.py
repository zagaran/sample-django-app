import mimetypes
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import FileResponse, Http404, HttpResponse

# START_FEATURE direct_upload
from django.core.files.storage import FileSystemStorage
from common.helpers import get_attachment_extension, remove_attachment_extension
# END_FEATURE direct_upload

from common.managers import UserManager

# START_FEATURE sentry
from sentry_sdk import capture_message

from common.permissions import ROLE_PERMISSIONS, UserRole
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

    role = models.CharField(max_length=128, default=UserRole.standard, choices=UserRole.choices)

    @property
    def permissions(self):
        return ROLE_PERMISSIONS[self.role]

    def has_permission(self, permission):
        return permission in self.permissions


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
    deleted_on = models.DateTimeField(null=True)

    def get_download_url(self, download_on_open: bool = True):
        extension = get_attachment_extension(self.file.name)
        filename = f"{remove_attachment_extension(self.name)}.{extension}".replace('"', '')
        content_type, _ = mimetypes.guess_type(self.file.name)
        s3_filename = self.file.name

        content_disposition = "attachment" if download_on_open else "inline"

        try:
            if isinstance(self.file.storage, FileSystemStorage):
                return FileResponse(
                    self.file.open(),
                    as_attachment=download_on_open,
                    filename=filename
                )

            # Download file directly from S3
            else:
                return self.file.storage.url(self.file.name, parameters={
                    "ResponseContentDisposition": f'{content_disposition}; filename="{filename}"',
                    "ResponseContentType": content_type or "application/octet-stream",
                })

        except Exception:
            capture_message(f"Failed to get object URL from S3 for ({self}) with path ({s3_filename})")
            raise Http404()

    def download_file(self) -> FileResponse | HttpResponse:
        return self.get_download_url(download_on_open=True)

    def view_file(self) -> FileResponse | HttpResponse:
        return self.get_download_url(download_on_open=False)
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