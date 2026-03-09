from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from app.models import Attachment
from common.constants import ATTACHMENT_PK_URL_KWARG
from common.serializers import UserSerializer


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
        if instance.file.storage.exists(instance.file.name):
            rep["size"] = instance.file.size
            rep["path"] = instance.file.name
        return rep
