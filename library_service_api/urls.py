from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("book.urls", namespace="book")),
    path("users/", include("user.urls", namespace="user")),
    path("borrowings/", include("borrowing.urls", namespace="borrowing")),
]
