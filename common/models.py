import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from common.managers import UserManager


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
def get_s3_path(instance, filename):
    return "%s/%s/%s" % (
        "uploads",
        instance.user_id,
        filename,
    )

class UploadFile(TimestampedModel):
    user = models.ForeignKey(User, related_name="files", on_delete=models.PROTECT)
    file = models.FileField(
        max_length=1024,
        upload_to=get_s3_path
    )

    class Meta:
        abstract = True
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
