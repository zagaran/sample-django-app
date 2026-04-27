# START_FEATURE direct_upload
from django import forms
from django.core.files.storage import default_storage
from django.core.files.storage.filesystem import FileSystemStorage
from django.db.models import QuerySet
from django.urls import reverse

from app.serializers import AttachmentSerializer


class DirectUploadFileInput(forms.SelectMultiple):
    queryset: QuerySet
    template_name = "widgets/direct_upload_file_input.html"

    def get_context(self, name, value, attrs):
        context: dict = super().get_context(name, value, attrs)
        context["upload_start_url"] = reverse("attachment_upload_start")
        context["storage_backend"] = ("filesystem" if isinstance(default_storage, FileSystemStorage) else "s3")
        context["queryset_json"] = [AttachmentSerializer(f).data for f in self.queryset.all()]
        return context


class DirectUploadFileField(forms.ModelMultipleChoiceField):
    """
    A field that allows for direct file uploads to S3 in form submissions.

    In order for the `DirectUploadFileField` to work properly in `ModelForm` instances,
    make sure that ForeignKey relationships between objects and attachments originate
    from the object and point to the attachment, not the other way around.
    """

    widget = DirectUploadFileInput

    def __init__(
        self,
        queryset: QuerySet,
        allowed_file_types: list[str] = [],
        multiple: bool = True,
        max_number_of_files: int | None = None,
        **kwargs,
    ):
        self.allowed_file_types = [ft if ft.startswith(".") else "." + ft for ft in allowed_file_types]
        self.multiple = multiple
        self.max_number_of_files = max_number_of_files
        super().__init__(queryset=queryset, **kwargs)
        self.widget.queryset = self.queryset

        if allowed_file_types:
            self.help_text = "Only the following file types are allowed: " + ", ".join(self.allowed_file_types)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['multiple'] = self.multiple
        attrs['required'] = self.required
        attrs['max_number_of_files'] = self.max_number_of_files
        attrs['allowed_file_types'] = self.allowed_file_types
        return attrs
# END_FEATURE direct_upload
