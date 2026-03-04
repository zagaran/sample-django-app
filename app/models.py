from django.db import models

from common.models import TimestampedModel, UploadFile, User


class SampleObject(TimestampedModel):
    created_by = models.ForeignKey(User, related_name="sample_objects", on_delete=models.PROTECT)
    name = models.CharField(max_length=512, unique=True)
    description = models.TextField(default="", blank=True)


# START_FEATURE direct_upload
class Attachment(UploadFile):
    sample_object = models.ManyToManyField("SampleObject", related_name="attachments")
# END_FEATURE direct_upload
