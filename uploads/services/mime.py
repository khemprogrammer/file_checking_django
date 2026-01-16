from django.conf import settings

def detect_mime_bytes(data):
    try:
        import magic
        return magic.from_buffer(data, mime=True)
    except Exception:
        return "application/octet-stream"

def detect_mime_file(path):
    try:
        import magic
        return magic.from_file(path, mime=True)
    except Exception:
        return "application/octet-stream"

