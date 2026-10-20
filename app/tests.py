from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from attachments_framework.models import Attachment
from app.models import SampleObject, SampleSubObject
from common.models import User


class SampleSubObjectTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="password")
        self.client.force_login(self.user)
        self.sample_object = SampleObject.objects.create(name="Parent", created_by=self.user)
        self.other_sample_object = SampleObject.objects.create(name="Other", created_by=self.user)

    def make_attachment(self, name="file.pdf", **kwargs):
        return Attachment.objects.create(
            name=name, file=f"test/{name}", user=self.user, upload_completed_on=timezone.now(), **kwargs
        )

    def make_sub_object(self, sample_object=None, attachment=None):
        return SampleSubObject.objects.create(
            sample_object=sample_object or self.sample_object,
            created_by=self.user,
            attachment=attachment or self.make_attachment(),
        )

    def url(self, name, sub_object=None, sample_object=None):
        args = [(sample_object or self.sample_object).id]
        if sub_object:
            args.append(sub_object.id)
        return reverse(name, args=args)

    def test_create(self):
        attachment = self.make_attachment()
        response = self.client.post(self.url("sample-sub-object-create"), {
            "description": "A sub object",
            "attachment": attachment.id,
        })
        self.assertRedirects(response, reverse("sample-object", args=[self.sample_object.id]))
        sub_object = SampleSubObject.objects.get()
        self.assertEqual(sub_object.sample_object, self.sample_object)
        self.assertEqual(sub_object.created_by, self.user)
        self.assertEqual(sub_object.attachment, attachment)
        self.assertEqual(sub_object.description, "A sub object")

    def test_create_requires_attachment(self):
        response = self.client.post(self.url("sample-sub-object-create"), {"description": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response.context["form"].errors)
        self.assertFalse(SampleSubObject.objects.exists())

    def test_attachment_cannot_be_shared(self):
        taken = self.make_sub_object().attachment
        response = self.client.post(self.url("sample-sub-object-create", sample_object=self.other_sample_object), {
            "attachment": taken.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response.context["form"].errors)
        self.assertEqual(SampleSubObject.objects.count(), 1)

    def test_deleted_attachment_cannot_be_used(self):
        attachment = self.make_attachment(deleted_on=timezone.now())
        response = self.client.post(self.url("sample-sub-object-create"), {"attachment": attachment.id})
        self.assertIn("attachment", response.context["form"].errors)

    def test_edit(self):
        sub_object = self.make_sub_object()
        # Keeping the current attachment is allowed
        response = self.client.post(self.url("sample-sub-object-edit", sub_object), {
            "description": "Edited",
            "attachment": sub_object.attachment_id,
        })
        self.assertEqual(response.status_code, 302)
        sub_object.refresh_from_db()
        self.assertEqual(sub_object.description, "Edited")

        # Replacing it with another sub object's attachment is not
        other = self.make_sub_object()
        response = self.client.post(self.url("sample-sub-object-edit", sub_object), {
            "attachment": other.attachment_id,
        })
        self.assertIn("attachment", response.context["form"].errors)

        new_attachment = self.make_attachment("new.pdf")
        self.client.post(self.url("sample-sub-object-edit", sub_object), {"attachment": new_attachment.id})
        sub_object.refresh_from_db()
        self.assertEqual(sub_object.attachment, new_attachment)

    def test_delete_keeps_attachment(self):
        sub_object = self.make_sub_object()
        self.assertEqual(self.client.get(self.url("sample-sub-object-delete", sub_object)).status_code, 200)
        response = self.client.post(self.url("sample-sub-object-delete", sub_object))
        self.assertRedirects(response, reverse("sample-object", args=[self.sample_object.id]))
        self.assertFalse(SampleSubObject.objects.exists())
        self.assertTrue(Attachment.objects.filter(pk=sub_object.attachment_id).exists())

    def test_views_scoped_to_sample_object(self):
        sub_object = self.make_sub_object()
        for name in ["sample-sub-object-edit", "sample-sub-object-delete"]:
            response = self.client.get(self.url(name, sub_object, sample_object=self.other_sample_object))
            self.assertEqual(response.status_code, 404)

    def test_attachments_listed_on_detail_and_dashboard(self):
        sub_object = self.make_sub_object(attachment=self.make_attachment("sub-attachment.pdf"))
        detail = self.client.get(reverse("sample-object", args=[self.sample_object.id]))
        self.assertContains(detail, "sub-attachment.pdf")
        self.assertContains(detail, self.url("sample-sub-object-edit", sub_object))
        dashboard = self.client.get(reverse("dashboard"))
        self.assertContains(dashboard, "sub-attachment.pdf")

    def test_upload_paths_extract_zips(self):
        # Every multi-file uploader extracts zips; the single-attachment sub object form uploads them as-is
        for url in [
            reverse("dashboard"),
            reverse("sample-object", args=[self.sample_object.id]),
            reverse("sample-object-create"),
            reverse("sample-object-edit", args=[self.sample_object.id]),
        ]:
            self.assertContains(self.client.get(url), ':extract-zips="true"', msg_prefix=url)
        self.assertNotContains(self.client.get(self.url("sample-sub-object-create")), "extract-zips")
