from django.db import models

from common.models import TimestampedModel, User

# START_FEATURE direct_upload
from attachments_framework.models import HasAttachmentsMixin
# END_FEATURE direct_upload


class SampleObject(
    # START_FEATURE direct_upload
    HasAttachmentsMixin,
    # END_FEATURE direct_upload
    TimestampedModel,
):
    created_by = models.ForeignKey(User, related_name="sample_objects", on_delete=models.PROTECT)

    name = models.CharField(max_length=512, unique=True)
    description = models.TextField(default="", blank=True)

    def __str__(self) -> str:
        return f'Sample Object {self.name}'
