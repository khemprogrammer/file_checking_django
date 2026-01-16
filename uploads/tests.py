from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import Upload
from django.test import override_settings
from io import BytesIO

class UploadTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="p")
        self.client = Client()
        self.client.login(username="u", password="p")

    def test_block_exe_extension(self):
        data = b"ABC"
        f = SimpleUploadedFile("evil.exe", data, content_type="application/octet-stream")
        resp = self.client.post(reverse("upload_file"), {"file": f})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Upload.objects.count(), 0)

    @patch("uploads.views.scan_file", return_value=("CLEAN", ""))
    def test_accept_png_valid(self, _scan):
        from PIL import Image
        bio = BytesIO()
        Image.new("RGB", (1, 1), (255, 0, 0)).save(bio, format="PNG")
        png = bio.getvalue()
        f = SimpleUploadedFile("image.png", png, content_type="image/png")
        resp = self.client.post(reverse("upload_file"), {"file": f}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Upload.objects.count(), 1)
        u = Upload.objects.first()
        self.assertEqual(u.scan_status, Upload.STATUS_CLEAN)
        self.assertTrue(u.file.name.startswith("secure_uploads/"))

    @patch("uploads.views.scan_file", return_value=("INFECTED", "EICAR"))
    def test_infected_file_deleted(self, _scan):
        import PyPDF2
        bio = BytesIO()
        writer = PyPDF2.PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.write(bio)
        pdf = bio.getvalue()
        f = SimpleUploadedFile("doc.pdf", pdf, content_type="application/pdf")
        resp = self.client.post(reverse("upload_file"), {"file": f}, follow=True)
        self.assertEqual(resp.status_code, 200)
        u = Upload.objects.first()
        self.assertEqual(u.scan_status, Upload.STATUS_INFECTED)
        self.assertFalse(bool(u.file))

    def test_mime_spoofing_rejected(self):
        bad = b"not an image"
        f = SimpleUploadedFile("img.png", bad, content_type="image/png")
        resp = self.client.post(reverse("upload_file"), {"file": f})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Upload.objects.count(), 0)

    def test_large_file_rejected(self):
        big = b"A" * (5 * 1024 * 1024 + 1)
        f = SimpleUploadedFile("big.pdf", big, content_type="application/pdf")
        resp = self.client.post(reverse("upload_file"), {"file": f})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Upload.objects.count(), 0)

    def test_logout_works_via_post(self):
        # Ensure authenticated
        resp = self.client.get(reverse("my_uploads"))
        self.assertEqual(resp.status_code, 200)
        # POST to logout
        resp = self.client.post(reverse("logout"), follow=True)
        self.assertEqual(resp.status_code, 200)
        # Access an authenticated page should redirect to login
        resp = self.client.get(reverse("my_uploads"), follow=True)
        self.assertIn("/accounts/login/", resp.redirect_chain[-1][0])

    @override_settings(SCAN_STRICT=False)
    @patch("uploads.views.scan_file", return_value=("ERROR", "network unreachable"))
    def test_scan_error_sets_pending_when_not_strict(self, _scan):
        from PIL import Image
        bio = BytesIO()
        Image.new("RGB", (1, 1), (255, 0, 0)).save(bio, format="PNG")
        png = bio.getvalue()
        f = SimpleUploadedFile("image.png", png, content_type="image/png")
        resp = self.client.post(reverse("upload_file"), {"file": f}, follow=True)
        self.assertEqual(resp.status_code, 200)
        u = Upload.objects.first()
        self.assertEqual(u.scan_status, Upload.STATUS_PENDING)

    def test_corrupt_png_rejected_if_pillow_available(self):
        data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
        f = SimpleUploadedFile("bad.png", data, content_type="image/png")
        resp = self.client.post(reverse("upload_file"), {"file": f})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Upload.objects.count(), 0)

    def test_corrupt_pdf_rejected_if_pypdf2_available(self):
        data = b"%PDF-1.4\n" + b"corrupt"
        f = SimpleUploadedFile("bad.pdf", data, content_type="application/pdf")
        resp = self.client.post(reverse("upload_file"), {"file": f})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Upload.objects.count(), 0)

    def test_signup_creates_user_and_logs_in(self):
        c = Client()
        resp = c.get(reverse("signup"))
        self.assertEqual(resp.status_code, 200)
        data = {
            "username": "newuser",
            "password1": "ValidPass123!",
            "password2": "ValidPass123!",
        }
        resp = c.post(reverse("signup"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        # Should land on My Uploads without redirect to login
        self.assertEqual(resp.resolver_match.view_name, "my_uploads")
