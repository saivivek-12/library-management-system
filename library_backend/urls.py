"""
URL configuration for library_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView
from library.views import CustomTokenObtainPairView
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("library.urls")),

    # JWT endpoints
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Library Management API",
        default_version='v1',
        description="Capstone Project API Documentation",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
]

# Frontend Template Routes
urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html'), name='login'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('books/', TemplateView.as_view(template_name='books.html'), name='books'),
    path('my-requests/', TemplateView.as_view(template_name='my-requests.html'), name='my_requests'),
    path('my-issues/', TemplateView.as_view(template_name='my-issues.html'), name='my_issues'),
    path('admin-dashboard/', TemplateView.as_view(template_name='admin-dashboard.html'), name='admin_dashboard'),
    path('admin-requests/', TemplateView.as_view(template_name='admin-requests.html'), name='admin_requests'),
    path('admin-students/', TemplateView.as_view(template_name='admin-students.html'), name='admin_students'),
    path('admin-student-detail/', TemplateView.as_view(template_name='admin-student-detail.html'), name='admin_student_detail'),
    path('admin-fines/', TemplateView.as_view(template_name='admin-fines.html'), name='admin_fines'),
    path('admin-logs/', TemplateView.as_view(template_name='admin-logs.html'), name='admin_logs'),
    path('admin-books/', TemplateView.as_view(template_name='admin-books.html'), name='admin_books'),
    path('forgot-password/', TemplateView.as_view(template_name='forgot-password.html'), name='forgot_password'),
    path('scan/issue/', TemplateView.as_view(template_name='scan_issue.html'), name='scan_issue'),
    path('scan/return/', TemplateView.as_view(template_name='scan_return.html'), name='scan_return'),
    path('scan/book/', TemplateView.as_view(template_name='scan_book.html'), name='scan_book'),
    path('fines/', TemplateView.as_view(template_name='fines.html'), name='fines'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('login/qr/', TemplateView.as_view(template_name='login_qr.html'), name='login-qr'),
    path('login/barcode/', TemplateView.as_view(template_name='login_barcode.html'), name='login-barcode'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)