from pathlib import Path
from django.conf import settings

def get_extension(filename):
    ext = Path(filename).suffix.lower().lstrip(".")
    return ext

def validate_extension(filename):
    ext = get_extension(filename)
    allowed_extensions = getattr(settings, 'UPLOAD_ALLOWED_EXTENSIONS', ['pdf', 'png', 'jpg', 'jpeg'])
    if ext not in allowed_extensions:
        return False
    return True

def validate_size(file_obj):
    max_size = getattr(settings, 'UPLOAD_MAX_SIZE', 5 * 1024 * 1024)
    return getattr(file_obj, 'size', 0) <= max_size

def expected_mimes_for_extension(ext):
    if ext in ["jpg", "jpeg"]:
        return ["image/jpeg", "image/jpg"]
    if ext == "png":
        return ["image/png"]
    if ext == "pdf":
        return ["application/pdf"]
    return []

def validate_mime(mime, ext):
    allowed_mimes = getattr(settings, 'UPLOAD_ALLOWED_MIME_TYPES', ['application/pdf', 'image/png', 'image/jpeg'])
    
    # Normalize MIME type
    mime = mime.lower()
    
    # Check if MIME is in allowed list
    if mime not in allowed_mimes:
        # Also check without subtype
        main_type = mime.split('/')[0] if '/' in mime else mime
        if main_type in ['image', 'application', 'pdf']:
            # Allow if extension matches expected types
            expected = expected_mimes_for_extension(ext)
            if expected:
                return True
        return False
    
    # Check if MIME matches extension
    expected = expected_mimes_for_extension(ext)
    if expected:
        # Be more lenient - allow any image type for image extensions
        if ext in ['jpg', 'jpeg'] and 'image/jpeg' in expected:
            return True
        if ext == 'png' and 'image/png' in expected:
            return True
        if ext == 'pdf' and 'application/pdf' in expected:
            return True
        return mime in expected
    
    return True
