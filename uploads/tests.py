from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import Upload

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
        png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00"*32
        f = SimpleUploadedFile("image.png", png, content_type="image/png")
        resp = self.client.post(reverse("upload_file"), {"file": f}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Upload.objects.count(), 1)
        u = Upload.objects.first()
        self.assertEqual(u.scan_status, Upload.STATUS_CLEAN)
        self.assertTrue(u.file.name.startswith("secure_uploads/"))

    @patch("uploads.views.scan_file", return_value=("INFECTED", "EICAR"))
    def test_infected_file_deleted(self, _scan):
        pdf = b"%PDF-1.4\n" + b"\x00"*64
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
