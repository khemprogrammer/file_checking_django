from django.contrib import admin
from .models import Upload
from .services.scanner import scan_file

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "original_filename", "size", "detected_mime", "scan_status", "created_at", "scanned_at")
    list_filter = ("scan_status", "detected_mime", "created_at")
    search_fields = ("original_filename", "user__username")
    actions = ["rescan_selected"]

    def rescan_selected(self, request, queryset):
        count_clean = 0
        count_infected = 0
        count_error = 0
        for upload in queryset:
            if not upload.file:
                continue
            status, message = scan_file(upload.file.path)
            if status == Upload.STATUS_INFECTED:
                try:
                    upload.file.delete(save=False)
                except Exception:
                    pass
                upload.file = None
                upload.save(update_fields=["file"])
                upload.mark_scanned(Upload.STATUS_INFECTED, message)
                count_infected += 1
            elif status == Upload.STATUS_CLEAN:
                upload.mark_scanned(Upload.STATUS_CLEAN, message)
                count_clean += 1
            else:
                upload.mark_scanned(Upload.STATUS_ERROR, message)
                count_error += 1
        self.message_user(request, f"Rescan complete: clean={count_clean}, infected={count_infected}, error={count_error}")
    rescan_selected.short_description = "Rescan selected uploads"
