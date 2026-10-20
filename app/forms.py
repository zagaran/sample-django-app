from crispy_forms.helper import Layout
from crispy_forms.layout import Fieldset
from django import forms
from django.http import HttpRequest

# START_FEATURE direct_upload
from attachments_framework.forms import AttachmentField, AttachmentsField, AttachmentsWidget
from attachments_framework.models import Attachment
# END_FEATURE direct_upload
from app.models import SampleObject, SampleSubObject
from common.forms import ActionFormMixin, CrispyFormMixin


# START_FEATURE direct_upload
class ZipExtractingAttachmentsWidget(AttachmentsWidget):
    """ Uploads the files inside zips instead of the zips themselves """
    template_name = "app/widgets/zip_extracting_attachments_input.html"


class ZipExtractingAttachmentsField(AttachmentsField):
    widget = ZipExtractingAttachmentsWidget
# END_FEATURE direct_upload


class SampleObjectBaseForm(CrispyFormMixin, ActionFormMixin, forms.ModelForm):
    request: HttpRequest

    # START_FEATURE direct_upload
    # `browse` lists every attachment so existing uploads can be selected, not just the ones already attached
    attachments = ZipExtractingAttachmentsField(required=False, browse=True, google_drive=True)
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


class SampleSubObjectBaseForm(CrispyFormMixin, ActionFormMixin, forms.ModelForm):
    request: HttpRequest

    # START_FEATURE direct_upload
    # A single attachment, so zips are uploaded as-is rather than extracted
    attachment = AttachmentField(
        browse=True,
        google_drive=True,
        error_messages={"invalid_choice": "That attachment is unavailable or already belongs to another sub object."},
    )
    # END_FEATURE direct_upload

    class Meta:
        model = SampleSubObject
        exclude = ['sample_object', 'created_by']

    layout = Layout(
        Fieldset(
            "Details",
            "description"
        ),
        # START_FEATURE direct_upload
        "attachment"
        # END_FEATURE direct_upload
    )

    def __init__(self, request: HttpRequest, sample_object: SampleObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.instance.sample_object = sample_object
        # START_FEATURE direct_upload
        # Sub objects can't share an attachment, so only offer the ones no other sub object holds
        taken = SampleSubObject.objects.exclude(pk=self.instance.pk).values("attachment")
        self.fields["attachment"].queryset = Attachment.objects.active().exclude(pk__in=taken)
        # END_FEATURE direct_upload


class SampleSubObjectCreateForm(SampleSubObjectBaseForm):
    action_title = "Create Sub Object of {instance.sample_object}"

    def save(self, commit=True):
        self.instance.created_by = self.request.user
        return super().save(commit)


class SampleSubObjectEditForm(SampleSubObjectBaseForm):
    action_title = "Edit {instance}"
