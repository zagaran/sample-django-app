from django.test import TestCase
# START_FEATURE crispy_forms
from django.contrib.messages import get_messages
from django.urls import reverse

from common.forms import SampleForm
# END_FEATURE crispy_forms

# Create your tests here.


# START_FEATURE crispy_forms
class SampleFormTests(TestCase):
    # TODO: delete me; these test the reference example in common.views.SampleFormView
    valid_data = {
        "email": "jane" + "@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "datetime_field_0": "2024-01-01",
        "datetime_field_1": "10:00",
    }

    def test_form_accepts_valid_input(self):
        form = SampleForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_missing_required_field(self):
        form = SampleForm(data={**self.valid_data, "email": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_get_renders_form(self):
        response = self.client.get(reverse("sample_form"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "common/sample_form.html")
        self.assertContains(response, 'name="email"')

    def test_valid_post_redirects_with_message(self):
        response = self.client.post(reverse("sample_form"), self.valid_data)
        self.assertRedirects(response, reverse("sample_form"))
        self.assertEqual([str(m) for m in get_messages(response.wsgi_request)], ["Sample form submitted"])

    def test_invalid_post_rerenders_with_errors(self):
        response = self.client.post(reverse("sample_form"), {**self.valid_data, "first_name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
# END_FEATURE crispy_forms
