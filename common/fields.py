from django import forms
from django.core.files.storage import default_storage
from django.core.files.storage.filesystem import FileSystemStorage
from django.shortcuts import reverse

from common.models import Attachment, User

# START_FEATURE direct_upload
class DirectUploadFileInput(forms.Widget):
    template_name = "widgets/multi_source_file_input.html"

    def get_context(self, name, value, attrs):
        context: dict = super().get_context(name, value, attrs)
        # context['max_file_size'] = FILE_UPLOAD_LIMIT
        context['min_files'] = self.attrs['min_files']
        context['max_files'] = self.attrs['max_files']
        context['allowed_file_types'] = self.attrs['allowed_file_types']
        context['upload_start_url'] = reverse("attachment_upload_start")
        context["storage_backend"] = ("filesystem" if isinstance(default_storage, FileSystemStorage) else "s3")
        return context

    def value_from_datadict(self, data, files, name):

        # `data` will always be a list of `InProgressFileUpload` uuids
        ids = data.getlist(name)

        # Attempt to get `Attachment` instances
        attachments = Attachment.objects.filter(id__in=ids)

        return attachments


class DirectUploadFileField(forms.Field):
    widget = DirectUploadFileInput

    def __init__(
        self,
        *,
        user: User,
        entra_enabled: bool = False,
        allowed_file_types: list[str] = [],
        multiple: bool = False,
        min_files: int | None = None,
        max_files: int | None = None,
        **kwargs,
    ):
        self.entra_enabled = entra_enabled
        self.allowed_file_types = [ft if ft.startswith(".") else "." + ft for ft in allowed_file_types]
        self.multiple = multiple
        self.min_files = min_files
        self.max_files = max_files
        super().__init__(**kwargs)

        if allowed_file_types:
            self.help_text = "Only the following file types are allowed: " + ", ".join(self.allowed_file_types)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['min_files'] = self.min_files
        attrs['max_files'] = self.max_files
        attrs['allowed_file_types'] = self.allowed_file_types
        return attrs
# END_FEATURE direct_upload
