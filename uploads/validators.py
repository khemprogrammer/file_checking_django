from pathlib import Path
from django.conf import settings

def get_extension(filename):
    ext = Path(filename).suffix.lower().lstrip(".")
    return ext

def validate_extension(filename):
    ext = get_extension(filename)
    if ext not in settings.UPLOAD_ALLOWED_EXTENSIONS:
        return False
    return True

def validate_size(file_obj):
    return getattr(file_obj, "size", 0) <= settings.UPLOAD_MAX_SIZE

def expected_mimes_for_extension(ext):
    if ext in ["jpg", "jpeg"]:
        return ["image/jpeg"]
    if ext == "png":
        return ["image/png"]
    if ext == "pdf":
        return ["application/pdf"]
    return []

def validate_mime(mime, ext):
    if mime not in settings.UPLOAD_ALLOWED_MIME_TYPES:
        return False
    expected = expected_mimes_for_extension(ext)
    if expected and mime not in expected:
        return False
    return True

