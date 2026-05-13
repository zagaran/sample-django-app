from django.core.files.storage import FileSystemStorage
from common.constants import StorageBackendType


def django_settings(request):
    from django.conf import settings
    from django.core.files.storage import default_storage
    return {
        "settings": settings,
        "storage_backend": (
            StorageBackendType.filesystem if isinstance(default_storage, FileSystemStorage)
            else StorageBackendType.s3
        )
    }
