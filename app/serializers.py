# START_FEATURE direct_upload
from app.constants import ATTACHMENT_PK_URL_KWARG
from django.utils.formats import date_format
from common.serializers import UserSerializer
from django.urls import reverse
from rest_framework import serializers

from app.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Attachment
        exclude = []

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["view_url"] = reverse('attachment_open', kwargs={
            ATTACHMENT_PK_URL_KWARG: instance.id,
        })
        rep["download_url"] = reverse('attachment_download', kwargs={
            ATTACHMENT_PK_URL_KWARG: instance.id,
        })
        rep["delete_url"] = reverse('attachment_delete', kwargs={
            ATTACHMENT_PK_URL_KWARG: instance.id,
        })
        rep["created_on"] = date_format(instance.created_on, format="DATETIME_FORMAT")
        if instance.upload_completed_on:
            rep["upload_completed_on"] = date_format(instance.upload_completed_on, format="DATETIME_FORMAT")
        if instance.file.storage.exists(instance.file.name):
            rep["size"] = instance.file.size
            rep["path"] = instance.file.name
        return rep
# END_FEATURE direct_upload
