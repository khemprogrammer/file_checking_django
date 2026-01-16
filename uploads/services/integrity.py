def check_image_integrity(file_obj):
    try:
        from PIL import Image
    except Exception:
        return None
    try:
        pos = file_obj.tell()
        img = Image.open(file_obj)
        img.verify()
        file_obj.seek(pos)
        return True
    except Exception:
        try:
            file_obj.seek(pos)
        except Exception:
            pass
        return False

def check_pdf_integrity(file_obj):
    try:
        import PyPDF2
    except Exception:
        return None
    try:
        pos = file_obj.tell()
        reader = PyPDF2.PdfReader(file_obj)
        _ = len(reader.pages)
        file_obj.seek(pos)
        return True
    except Exception:
        try:
            file_obj.seek(pos)
        except Exception:
            pass
        return False

