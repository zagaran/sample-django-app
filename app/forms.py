from crispy_forms.helper import Layout
from crispy_forms.layout import Fieldset
from django import forms
from django.http import HttpRequest
from app.models import Attachment, SampleObject
from common.fields import DirectUploadFileField
from common.forms import CrispyFormMixin


class SampleObjectBaseForm(CrispyFormMixin, forms.ModelForm):
    request: HttpRequest

    class Meta:
        model = SampleObject
        exclude = ['created_by']

    layout = Layout(
        Fieldset("Details", "name", "description"),
        Fieldset("Attachments", "attachments")
    )

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request


class SampleObjectCreateForm(SampleObjectBaseForm):
    attachments = DirectUploadFileField(queryset=Attachment.objects.all())

    def save(self, commit=True):
        self.instance.created_by = self.request.user
        return super().save(commit)


class SampleObjectEditForm(SampleObjectBaseForm):
    attachments = DirectUploadFileField(queryset=Attachment.objects.all())
    pass
