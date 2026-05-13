# START_FEATURE direct_upload
from django.db.models import TextChoices


class StorageBackendType(TextChoices):
    s3 = ("s3", "S3 Bucket")
    filesystem = ("filesystem", "Local Filesystem Storage")
# END_FEATURE direct_upload
