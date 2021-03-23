# START_FEATURE crispy_forms
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CrispyFormMixin(object):
    submit_label = "Save"
    form_action = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = self.form_action
        self.helper.add_input(Submit("submit", self.submit_label))
# END_FEATURE crispy_forms
