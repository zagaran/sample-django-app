# START_FEATURE direct_upload
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage


def create_presigned_upload_url(object_name: str, expiration: int = 3600):
    """
    Generate a presigned URL to upload an S3 object via PUT
    (see https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)
    """
    if isinstance(default_storage, S3Boto3Storage):
        return default_storage.url(object_name, http_method="PUT", expire=expiration)
    else:
        raise Exception(f"Cannot create a presigned upload URL for {type(default_storage)} storage")
# END_FEATURE direct_upload
