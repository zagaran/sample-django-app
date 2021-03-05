import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
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
    
    def __str__(self):
        return self.email

# START_FEATURE django_storages
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
# from storages.backends.s3boto3 import S3Boto3Storage
# 
# def get_file_storage():
#     if not settings.DEBUG:
#         return S3Boto3Storage(bucket=settings.AWS_STORAGE_BUCKET_NAME)
#     else:
#         return FileSystemStorage(location='media/uploads/')
# 
# def get_s3_path(instance, filename):
#     return "%s/%s/%s" % (
#         "uploads",
#         instance.user_id,
#         filename,
#     )
# 
# class UploadFile(TimestampedModel):
#     user = models.ForeignKey(User, related_name="files", on_delete=models.PROTECT)
#     file = models.FileField(
#         max_length=1024,
#         storage=get_file_storage(),
#         upload_to=get_s3_path
#     )
# END_FEATURE django_storages
