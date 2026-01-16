from django.shortcuts import render, redirect
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import UploadForm
from .models import Upload
from .services.scanner import scan_file
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

logger = logging.getLogger("uploads")

@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(user=request.user, commit=True)
            status, message = scan_file(upload.file.path)
            if status == Upload.STATUS_INFECTED:
                try:
                    upload.file.delete(save=False)
                except Exception:
                    pass
                upload.file = None
                upload.save(update_fields=["file"])
                upload.mark_scanned(Upload.STATUS_INFECTED, message)
                logger.info("infected upload blocked user=%s name=%s size=%s mime=%s msg=%s", request.user.id, upload.original_filename, upload.size, upload.detected_mime, message)
                messages.error(request, "Upload blocked: file infected")
            elif status == Upload.STATUS_CLEAN:
                upload.mark_scanned(Upload.STATUS_CLEAN, message)
                logger.info("clean upload stored user=%s name=%s size=%s mime=%s", request.user.id, upload.original_filename, upload.size, upload.detected_mime)
                messages.success(request, "File uploaded and scanned clean")
            else:
                if getattr(settings, "SCAN_STRICT", False):
                    upload.mark_scanned(Upload.STATUS_ERROR, message)
                    logger.info("scan error recorded user=%s name=%s size=%s mime=%s msg=%s", request.user.id, upload.original_filename, upload.size, upload.detected_mime, message)
                    messages.warning(request, "Scan error recorded")
                else:
                    upload.mark_scanned(Upload.STATUS_PENDING, f"Scan unavailable: {message}")
                    logger.info("scan unavailable user=%s name=%s size=%s mime=%s msg=%s", request.user.id, upload.original_filename, upload.size, upload.detected_mime, message)
                    messages.info(request, "Scan temporarily unavailable; file quarantined")
            return redirect("my_uploads")
        else:
            messages.error(request, "Upload failed")
    else:
        form = UploadForm()
    return render(request, "uploads/upload_form.html", {"form": form})

@login_required
def my_uploads(request):
    qs = Upload.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "uploads/upload_list.html", {"uploads": qs})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. You are now logged in.")
            return redirect("my_uploads")
        else:
            messages.error(request, "Signup failed. Please correct the errors.")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
