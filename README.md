# Secure File Upload (Django)

Secure, auditable file uploads with authentication, strict validation, MIME sniffing, integrity checks, and multi-backend malware scanning.

## Features
- Authentication: login, logout, and signup with auto-login
- Allowed types: PDF, PNG, JPG/JPEG; size ≤ 5 MB
- Content validation: libmagic-based MIME sniffing
- Integrity checks: Pillow for images, PyPDF2 for PDFs (rejects corrupt files)
- Malware scanning: tries clamd → clamscan → Windows Defender (MpCmdRun)
- Safe storage: UUID filenames under `media/secure_uploads/`
- Quarantine: files marked PENDING when scanner is unavailable (no download link)
- Admin: rescan selected uploads, see statuses and metadata
- Logging: structured file-audit logs in `upload_audit.log`

## Requirements
- Python 3.10+
- See `requirements.txt` for Python packages
- Optional scanners:
  - ClamAV daemon (clamd) on `127.0.0.1:3310`
  - ClamAV CLI (`clamscan`)
  - Windows Defender CLI (`MpCmdRun.exe`) on Windows

## Quickstart
### 1) Setup
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Database and admin
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3) Run
```bash
python manage.py runserver
# Visit: http://127.0.0.1:8000/
```

## Usage
- Signup: /accounts/signup/
- Login: /accounts/login/
- Upload: /
- My Uploads: /uploads/
- Admin: /admin/

## Scanner Options
- clamd (recommended):
  - Host: `127.0.0.1`, Port: `3310`
  - Set env vars if needed: `CLAMAV_HOST`, `CLAMAV_PORT`
- clamscan (CLI fallback):
  - Install ClamAV and run `freshclam` to update definitions
- Windows Defender (Windows fallback):
  - The app auto-locates `MpCmdRun.exe` in typical Defender locations

## Behavior
- CLEAN: file stored and link visible
- INFECTED: file deleted, status INFECTED
- Scanner unavailable:
  - Dev-friendly default: `PENDING` and quarantined (no link)
  - Strict mode: set `SCAN_STRICT=1` to mark as `ERROR`

## Configuration
Set environment variables as needed:
- `CLAMAV_HOST` (default `127.0.0.1`)
- `CLAMAV_PORT` (default `3310`)
- `SCAN_STRICT` (`0` or `1`; default `0`)

## Tests
```bash
python manage.py test -v 2
```
Includes validation, integrity, scanner behavior, and auth flow tests.

## Production Notes
- Set `DEBUG=False` and a strong `SECRET_KEY`
- Configure a real static files pipeline and `STATIC_ROOT`
- Serve media securely; link files only when status is `CLEAN`
- Prefer running clamd and queue scans asynchronously for scale

## Project Structure Highlights
- Settings: `secure_upload/settings.py`
- URLs: `secure_upload/urls.py`
- Uploads app:
  - Models, views, forms, validators
  - Services: `mime.py`, `scanner.py`, `integrity.py`
  - Templates: base, upload form/list, auth pages
  - Static CSS: `uploads/static/uploads/style.css`

