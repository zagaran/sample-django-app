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


# START_FEATURE crispy_forms
class SampleForm(CrispyFormMixin, forms.Form):
    # TODO: delete me; this is just a reference example
    is_company = forms.CharField(label="company", required=False, widget=forms.CheckboxInput())
    email = forms.EmailField(
        label="email", max_length=30, required=True, widget=forms.TextInput(), help_text="Insert your email"
    )
    first_name = forms.CharField(label="first name", max_length=5, required=True, widget=forms.TextInput())
    last_name = forms.CharField(label="last name", max_length=5, required=True, widget=forms.TextInput())
    datetime_field = forms.SplitDateTimeField(label="date time", widget=forms.SplitDateTimeWidget())

    def clean(self):
        super().clean()
        password1 = self.cleaned_data.get("password1", None)
        password2 = self.cleaned_data.get("password2", None)
        if not password1 and not password2 or password1 != password2:
            raise forms.ValidationError("Passwords dont match")
        return self.cleaned_data
# END_FEATURE crispy_forms
