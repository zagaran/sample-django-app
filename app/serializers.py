# START_FEATURE direct_upload
from app.constants import ATTACHMENT_PK_URL_KWARG
from django.utils.formats import date_format
from common.serializers import UserSerializer
from django.urls import reverse
from rest_framework import serializers

from app.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    view_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()
    created_on = serializers.SerializerMethodField()
    upload_completed_on = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        exclude = []

    def get_view_url(self, instance):
        return reverse('attachment_open', kwargs={ATTACHMENT_PK_URL_KWARG: instance.id})

    def get_download_url(self, instance):
        return reverse('attachment_download', kwargs={ATTACHMENT_PK_URL_KWARG: instance.id})

    def get_delete_url(self, instance):
        return reverse('attachment_delete', kwargs={ATTACHMENT_PK_URL_KWARG: instance.id})

    def get_created_on(self, instance):
        return date_format(instance.created_on, format="DATETIME_FORMAT")

    def get_upload_completed_on(self, instance):
        return date_format(instance.upload_completed_on, format="DATETIME_FORMAT")

    def get_size(self, instance):
        return instance.file.size

    def get_path(self, instance):
        return instance.file.name
# END_FEATURE direct_upload
