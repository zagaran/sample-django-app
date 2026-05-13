# START_FEATURE crispy_forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Button, Submit
from django.db.models import Model


class CrispyFormMixin:
    submit_label: str = "Save"
    cancel_label: str = "Cancel"
    form_action: str = ""
    form_tag: bool = True
    default_actions: bool = True
    layout: Layout | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = self.form_action
        if self.layout is not None:
            self.helper.layout = self.layout
        if self.default_actions:
            self.helper.add_input(Submit("submit", self.submit_label))
            self.helper.add_input(Button("cancel", self.cancel_label,
                                  css_class="btn-secondary", onclick="history.back()"))
# END_FEATURE crispy_forms


class ActionFormMixin:
    instance: type[Model]
    action_title: str = "Perform Action"

    @property
    def action_title_formatted(self):
        return self.action_title.format(instance=self.instance)
