from django.db import models

from common.models import TimestampedModel, User

# START_FEATURE direct_upload
from attachments_framework.models import Attachment, HasAttachmentsMixin
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


class SampleSubObject(TimestampedModel):
    sample_object = models.ForeignKey(SampleObject, related_name="sub_objects", on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name="sample_sub_objects", on_delete=models.PROTECT)

    description = models.TextField(default="", blank=True)
    # START_FEATURE direct_upload
    # One-to-one so that no two sub objects can share an attachment
    attachment = models.OneToOneField(Attachment, related_name="sample_sub_object", on_delete=models.PROTECT)
    # END_FEATURE direct_upload

    class Meta:
        ordering = ["created_on"]

    def __str__(self) -> str:
        return f'Sub Object of {self.sample_object}'

    # START_FEATURE direct_upload
    @property
    def active_attachment(self) -> Attachment | None:
        """ The attachment, unless it has since been deleted (e.g. from the dashboard) """
        attachment = self.attachment
        if attachment.is_deleted or not attachment.is_upload_completed:
            return None
        return attachment
    # END_FEATURE direct_upload
