# START_FEATURE crispy_forms
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class SampleForm(forms.ModelForm):
    # TODO: delete me; this is just a reference example
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Submit"))
# END_FEATURE crispy_forms
