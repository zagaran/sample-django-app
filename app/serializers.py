from rest_framework import serializers
from app.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        exclude = ['user']
