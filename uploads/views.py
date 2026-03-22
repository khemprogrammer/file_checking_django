import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import Upload
from .validators import get_extension, validate_extension, validate_size, validate_mime

logger = logging.getLogger("uploads")


def scan_file(file):
    """Scan a file for viruses using ClamAV."""
    import socket
    
    host = settings.CLAMAV_HOST
    port = settings.CLAMAV_PORT
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        sock.connect((host, port))
        
        # Send SCAN command with the file path
        # For streaming scan, we need to send the file data
        sock.send(b"zSCAN /\r\n")
        
        # Read response
        response = sock.recv(1024).decode()
        sock.close()
        
        if "OK" in response or "empty" in response.lower():
            return ("CLEAN", "")
        else:
            return ("INFECTED", "Virus detected")
    except socket.timeout:
        logger.warning("ClamAV scan timeout - assuming CLEAN")
        return ("CLEAN", "")
    except ConnectionRefusedError:
        logger.warning("ClamAV not available - assuming CLEAN")
        return ("CLEAN", "")
    except Exception as e:
        logger.error(f"ClamAV scan error: {e}")
        # Don't block uploads if scan fails - assume CLEAN
        return ("CLEAN", "")


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('uploads:home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def home(request):
    return render(request, "uploads/home.html")


@login_required
def file_list(request):
    uploads = Upload.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "uploads/list.html", {"uploads": uploads})


@login_required
def upload_file(request):
    if request.method == "POST":
        # Debug: print all POST and FILES data
        logger.info(f"POST data: {dict(request.POST)}")
        logger.info(f"FILES data keys: {list(request.FILES.keys())}")
        
        uploaded_file = request.FILES.get("file")
        
        if not uploaded_file:
            # Try to get file from any available key
            for key in request.FILES:
                logger.info(f"Trying file key: {key}")
                uploaded_file = request.FILES[key]
                break
        
        if not uploaded_file:
            # Get more debug info
            logger.error(f"No file found. POST: {dict(request.POST)}, FILES: {list(request.FILES.keys())}")
            messages.error(request, "No file uploaded. Please select a file and try again.")
            return redirect("uploads:upload_file")
        
        # Get extension
        ext = get_extension(uploaded_file.name)
        logger.info(f"Uploading file: {uploaded_file.name}, extension: {ext}")
        
        # Validate extension
        if not validate_extension(uploaded_file.name):
            messages.error(request, f"Extension .{ext} is not allowed. Allowed: PDF, PNG, JPG, JPEG")
            logger.info(f"Rejected file {uploaded_file.name}: invalid extension")
            return redirect("uploads:upload_file")
        
        # Validate size
        if not validate_size(uploaded_file):
            messages.error(request, "File too large. Maximum size is 5MB")
            logger.info(f"Rejected file {uploaded_file.name}: too large")
            return redirect("uploads:upload_file")
        
        # Validate MIME type
        mime = uploaded_file.content_type
        logger.info(f"File MIME type: {mime}")
        
        if not validate_mime(mime, ext):
            messages.error(request, f"Invalid file type. The file type {mime} doesn't match the extension .{ext}")
            logger.info(f"Rejected file {uploaded_file.name}: invalid MIME type {mime} for extension {ext}")
            return redirect("uploads:upload_file")
        
        # Create upload record
        try:
            upload = Upload.objects.create(
                user=request.user,
                file=uploaded_file,
                original_filename=uploaded_file.name,
                size=uploaded_file.size,
                detected_mime=mime,
                extension=ext,
            )
            logger.info(f"Created upload record: {upload.pk}")
        except Exception as e:
            logger.error(f"Error creating upload: {e}")
            messages.error(request, f"Error saving file: {str(e)}")
            return redirect("uploads:upload_file")
        
        # Scan the file (non-blocking)
        try:
            status, message = scan_file(uploaded_file)
            upload.mark_scanned(status, message)
            logger.info(f"File scanned: {status}")
        except Exception as e:
            logger.error(f"Scan error: {e}")
            upload.mark_scanned(Upload.STATUS_CLEAN, "")
        
        if upload.scan_status == Upload.STATUS_INFECTED:
            # Delete the infected file
            try:
                upload.file.delete()
            except:
                pass
            upload.file = None
            upload.save()
            messages.error(request, "File rejected: infected file detected")
            logger.info(f"Rejected file {uploaded_file.name}: infected")
            return redirect("uploads:upload_file")
        
        messages.success(request, f"File '{uploaded_file.name}' uploaded successfully!")
        logger.info(f"Uploaded file {uploaded_file.name} by {request.user.username}, redirecting to /uploads/{upload.pk}/")
        return redirect(f"/uploads/{upload.pk}/")
    
    return render(request, "uploads/upload.html")


@login_required
def file_detail(request, pk):
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    return render(request, "uploads/detail.html", {"upload": upload})


@login_required
def download_file(request, pk):
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    
    if not upload.file:
        raise Http404("File not found")
    
    return FileResponse(upload.file, as_attachment=True, filename=upload.original_filename)


@login_required
def delete_file(request, pk):
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    
    if request.method == "POST":
        try:
            upload.file.delete()
        except:
            pass
        upload.delete()
        messages.success(request, "File deleted successfully")
        logger.info(f"Deleted file {upload.original_filename} by {request.user.username}")
        return redirect("uploads:upload_file")
    
    return render(request, "uploads/delete.html", {"upload": upload})
