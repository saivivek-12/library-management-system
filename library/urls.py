from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BookViewSet, StudentViewSet, IssueViewSet
from .views import BookRequestViewSet
from .views import AdminDashboardViewSet
from .views import StudentSignupView, ForgotPasswordView
from .views import UnpaidFinesViewSet, AuditLogViewSet, NotificationViewSet, WaitlistViewSet
from .views import BookCopyViewSet, QRIssueView, QRReturnView, QRLoginView, NameLoginView, BarcodeLoginView
from .views import BookDemandViewSet, LibraryAssistantView

router = DefaultRouter()
router.register(r"authors", AuthorViewSet)
router.register(r"books", BookViewSet)
router.register(r"students", StudentViewSet)
router.register(r"issues", IssueViewSet)
router.register(r"requests", BookRequestViewSet)
router.register(r"admin-dashboard", AdminDashboardViewSet, basename="admin-dashboard")
router.register(r"reports/unpaid-fines", UnpaidFinesViewSet, basename="unpaid-fines")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-logs")
router.register(r"notifications", NotificationViewSet, basename="notifications")
router.register(r"waitlists", WaitlistViewSet, basename="waitlists")
router.register(r"book-copies", BookCopyViewSet, basename="book-copies")
router.register(r"demands", BookDemandViewSet, basename="demands")

urlpatterns = [
    path("signup/", StudentSignupView.as_view(), name="signup"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("qr/issue/", QRIssueView.as_view(), name="qr-issue"),
    path("qr/return/", QRReturnView.as_view(), name="qr-return"),
    path("qr-login/", QRLoginView.as_view(), name="qr_login"),
    path("name-login/", NameLoginView.as_view(), name="name_login"),
    path("barcode-login/", BarcodeLoginView.as_view(), name="barcode-login"),
    path("library-assistant/", LibraryAssistantView.as_view(), name="library-assistant"),
    path("", include(router.urls)),
]