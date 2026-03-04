from django import forms
from django.http import HttpRequest
from app.models import SampleObject
from common.fields import DirectUploadFileField
from common.forms import CrispyFormMixin


class SampleObjectBaseForm(CrispyFormMixin, forms.ModelForm):
    request: HttpRequest

    class Meta:
        model = SampleObject
        exclude = ['created_by']

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request


class SampleObjectCreateForm(SampleObjectBaseForm):
    attachments = DirectUploadFileField()

    def save(self, commit=True):
        self.instance.created_by = self.request.user
        return super().save(commit)


class SampleObjectEditForm(SampleObjectBaseForm):
    pass
