from crispy_forms.helper import Layout
from crispy_forms.layout import Fieldset
from django import forms
from django.http import HttpRequest
from app.models import Attachment, SampleObject
from common.fields import DirectUploadFileField
from common.forms import ActionFormMixin, CrispyFormMixin


class SampleObjectBaseForm(CrispyFormMixin, ActionFormMixin, forms.ModelForm):
    request: HttpRequest
    attachments = DirectUploadFileField(queryset=Attachment.objects.all())

    class Meta:
        model = SampleObject
        exclude = ['created_by']

    layout = Layout(
        Fieldset(
            "Details",
            "name",
            "description"
        ),
        Fieldset(
            "Attachments",
            "attachments"
        )
    )

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request


class SampleObjectCreateForm(SampleObjectBaseForm):
    action_title = "Create Sample Object"

    def save(self, commit=True):
        self.instance.created_by = self.request.user
        return super().save(commit)


class SampleObjectEditForm(SampleObjectBaseForm):
    action_title = "Edit {item}"
