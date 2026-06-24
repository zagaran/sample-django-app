# START_FEATURE direct_upload
from django import forms
from django.conf import settings
from django.db.models import QuerySet
from django.urls import reverse

from app.serializers import AttachmentSerializer


class DirectUploadFileInput(forms.SelectMultiple):
    queryset: QuerySet
    template_name = "widgets/direct_upload_file_input.html"

    def get_context(self, name, value, attrs):
        context: dict = super().get_context(name, value, attrs)
        context["upload_start_url"] = reverse("attachment_upload_start")
        context['queryset_json'] = AttachmentSerializer(
            self.queryset.filter(upload_completed_on__isnull=False),
            many=True,
        ).data
        context["storage_backend"] = settings.DEFAULT_STORAGE_TYPE
        return context


class DirectUploadFileField(forms.ModelMultipleChoiceField):
    """
    A field that allows for direct file uploads to S3 in form submissions.
    """

    widget = DirectUploadFileInput

    def __init__(
        self,
        queryset: QuerySet,
        allowed_file_types: list[str] = [],
        max_number_of_files: int | None = None,
        max_file_size: int | None = None,
        **kwargs,
    ):
        self.allowed_file_types = [ft if ft.startswith(".") else "." + ft for ft in allowed_file_types]
        self.max_number_of_files = max_number_of_files

        # Max file size in bytes
        self.max_file_size = max_file_size

        super().__init__(queryset=queryset, **kwargs)
        self.widget.queryset = self.queryset

        if allowed_file_types:
            self.help_text = "Only the following file types are allowed: " + ", ".join(self.allowed_file_types)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['required'] = self.required
        attrs['max_number_of_files'] = self.max_number_of_files
        attrs['max_file_size'] = self.max_file_size
        attrs['allowed_file_types'] = self.allowed_file_types
        return attrs
# END_FEATURE direct_upload
