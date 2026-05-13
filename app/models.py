from django.db import models

from common.models import TimestampedModel, UploadFile, User


class SampleObject(TimestampedModel):
    created_by = models.ForeignKey(User, related_name="sample_objects", on_delete=models.PROTECT)

    # START_FEATURE direct_upload
    attachments = models.ManyToManyField("Attachment", related_name="sample_objects")
    # END_FEATURE direct_upload

    name = models.CharField(max_length=512, unique=True)
    description = models.TextField(default="", blank=True)

    def __str__(self) -> str:
        return f'Sample Object {self.name}'

    def get_attachments(self):
        qs = self.attachments.prefetch_related('user')
        return [
            attachment for attachment in qs
            if not attachment.deleted_on
        ]


# START_FEATURE direct_upload
class Attachment(UploadFile):
    pass
# END_FEATURE direct_upload
