# START_FEATURE direct_upload
import boto3

from django.conf import settings

from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage


def create_presigned_upload_url(object_name: str, expiration: int = 3600):
    """
    Generate a presigned URL to upload an S3 object
    (see https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    response = None
    if isinstance(default_storage, S3Boto3Storage):
        response = s3_client.generate_presigned_post(
            settings.AWS_STORAGE_BUCKET_NAME,
            object_name,
            ExpiresIn=expiration
        )

        # The response contains the presigned URL and required fields
        return response

    else:
        raise Exception(f"Cannot create a presigned upload URL for {type(default_storage)} storage")

# END_FEATURE direct_upload
