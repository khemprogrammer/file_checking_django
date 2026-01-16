from django import forms
from .models import Upload
from .validators import validate_extension, validate_size, validate_mime, get_extension
from .services.mime import detect_mime_bytes
from .services.integrity import check_image_integrity, check_pdf_integrity

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ["file"]

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f:
            raise forms.ValidationError("No file provided")
        if not validate_size(f):
            raise forms.ValidationError("File exceeds size limit")
        original_name = getattr(f, "name", "")
        if not validate_extension(original_name):
            raise forms.ValidationError("File type not allowed")
        data = f.read(4096)
        mime = detect_mime_bytes(data)
        f.seek(0)
        ext = get_extension(original_name)
        if not validate_mime(mime, ext):
            raise forms.ValidationError("File content type is not allowed")
        if ext in ("jpg", "jpeg", "png"):
            ok = check_image_integrity(f)
            if ok is False:
                raise forms.ValidationError("Image appears corrupted or malformed")
        elif ext == "pdf":
            ok = check_pdf_integrity(f)
            if ok is False:
                raise forms.ValidationError("PDF appears corrupted or malformed")
        self._detected_mime = mime
        self._extension = ext
        self._size = getattr(f, "size", 0)
        self._original_name = original_name
        return f

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        instance.user = user
        instance.original_filename = getattr(self, "_original_name", "")
        instance.size = getattr(self, "_size", 0)
        instance.detected_mime = getattr(self, "_detected_mime", "")
        instance.extension = getattr(self, "_extension", "")
        if commit:
            instance.save()
            self.save_m2m()
        return instance
