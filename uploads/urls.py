from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_file, name="upload_file"),
    path("uploads/", views.my_uploads, name="my_uploads"),
    path("accounts/signup/", views.signup, name="signup"),
]
