from uuid import uuid4
from django.db import models
from django.conf import settings
from django.utils import timezone

def upload_path(instance, filename):
    ext = instance.extension or "bin"
    return f"secure_uploads/{uuid4().hex}.{ext}"

class Upload(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_CLEAN = "CLEAN"
    STATUS_INFECTED = "INFECTED"
    STATUS_ERROR = "ERROR"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CLEAN, "Clean"),
        (STATUS_INFECTED, "Infected"),
        (STATUS_ERROR, "Error"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_path)
    original_filename = models.CharField(max_length=255)
    size = models.BigIntegerField()
    detected_mime = models.CharField(max_length=100)
    extension = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    scanned_at = models.DateTimeField(null=True, blank=True)
    scan_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    scan_message = models.TextField(blank=True)

    def mark_scanned(self, status, message=""):
        self.scan_status = status
        self.scan_message = message or ""
        self.scanned_at = timezone.now()
        self.save(update_fields=["scan_status", "scan_message", "scanned_at"])

