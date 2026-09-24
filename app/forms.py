from crispy_forms.helper import Layout
from crispy_forms.layout import Fieldset
from django import forms
from django.http import HttpRequest

# START_FEATURE direct_upload
from attachments_framework.forms import AttachmentsField
# END_FEATURE direct_upload
from app.models import SampleObject
from common.forms import ActionFormMixin, CrispyFormMixin


class SampleObjectBaseForm(CrispyFormMixin, ActionFormMixin, forms.ModelForm):
    request: HttpRequest

    # START_FEATURE direct_upload
    # `browse` lists every attachment so existing uploads can be selected, not just the ones already attached
    attachments = AttachmentsField(required=False, browse=True)
    # END_FEATURE direct_upload

    class Meta:
        model = SampleObject
        exclude = ['created_by']

    layout = Layout(
        Fieldset(
            "Details",
            "name",
            "description"
        ),
        # START_FEATURE direct_upload
        "attachments"
        # END_FEATURE direct_upload
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
    action_title = "Edit {instance}"
