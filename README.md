# Secure File Upload System

A Django-based secure file upload system with virus scanning, user authentication, and a modern responsive UI.

## Features

- **User Authentication**: Login, logout, and user registration (signup)
- **Secure File Upload**: Upload PDF, PNG, JPG, JPEG, GIF, BMP, WEBP files (max 5MB)
- **Virus Scanning**: Automatic virus scanning using ClamAV
- **File Management**: View, download, and delete uploaded files
- **MIME Type Validation**: Strict validation to prevent file type spoofing
- **Audit Logging**: All upload activities are logged
- **Responsive UI**: Modern Bootstrap 5 based design with premium styling

## Requirements

- Python 3.10+
- Django 5.0+
- ClamAV (optional, for virus scanning)

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd secure_file_project
```

### 2. Create virtual environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Database setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the server
```bash
python manage.py runserver
```

## Configuration

Environment variables (optional):
- `CLAMAV_HOST` - ClamAV server host (default: 127.0.0.1)
- `CLAMAV_PORT` - ClamAV server port (default: 3310)
- `SCAN_STRICT` - Set to "1" to reject files when scanner is unavailable (default: "0")

## Usage

- **Home Page**: http://127.0.0.1:8000/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Sign Up**: http://127.0.0.1:8000/signup/
- **Upload**: http://127.0.0.1:8000/uploads/
- **My Files**: http://127.0.0.1:8000/uploads/list/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### Default Admin Credentials
- Username: `admin`
- Password: `khem123456`

## Project Structure

```
secure_file_project/
├── manage.py              # Django management script
├── db.sqlite3             # SQLite database
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── upload_audit.log       # Upload audit log
├── media/                 # Uploaded files storage
│   └── secure_uploads/    # Secure file storage
├── secure_upload/         # Django project settings
│   ├── settings.py        # Project settings
│   ├── urls.py             # URL configuration
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
└── uploads/               # Main application
    ├── models.py           # Database models
    ├── views.py           # View functions
    ├── urls.py            # URL routing
    ├── validators.py      # File validators
    ├── tests.py           # Unit tests
    ├── migrations/        # Database migrations
    └── templates/         # HTML templates
        ├── base.html
        ├── registration/
        │   ├── login.html
        │   └── signup.html
        └── uploads/
            ├── home.html
            ├── upload.html
            ├── list.html
            ├── detail.html
            └── delete.html
```

## Testing

```bash
python manage.py test -v 2
```

## License

MIT License
