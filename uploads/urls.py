from django.urls import path
from . import views

app_name = "uploads"

urlpatterns = [
    path("", views.home, name="home"),
    path("uploads/", views.upload_file, name="upload_file"),
    path("uploads/list/", views.file_list, name="file_list"),
    path("uploads/<int:pk>/", views.file_detail, name="file_detail"),
    path("uploads/<int:pk>/download/", views.download_file, name="download_file"),
    path("uploads/<int:pk>/delete/", views.delete_file, name="delete_file"),
    path("signup/", views.signup, name="signup"),
]
