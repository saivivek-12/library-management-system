from rest_framework import serializers
from .models import (
    Author, Book, Student, Issue, BookRequest, BookCopy, 
    IssueTransaction, Waitlist, BookSummary, BookDemand,
    AuditLog, Notification
)

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"

class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)

    class Meta:
        model = Book
        fields = "__all__"

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Student
        fields = "__all__"
        read_only_fields = ("user",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            is_admin = getattr(request.user, "is_staff", False) or \
                       (hasattr(request.user, "student") and request.user.student.role in ["LIBRARIAN", "SUPER_ADMIN"])
            if not is_admin:
                self.fields["is_active"].read_only = True
                self.fields["role"].read_only = True

class AdminStudentSummarySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    active_issues_count = serializers.IntegerField(read_only=True)
    overdue_issues_count = serializers.IntegerField(read_only=True)
    total_unpaid_fine = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_requests = serializers.IntegerField(read_only=True)

    class Meta:
        model = Student
        fields = "__all__"

class IssueSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    is_overdue = serializers.ReadOnlyField()
    fine = serializers.ReadOnlyField()

    class Meta:
        model = Issue
        fields = "__all__"
        read_only_fields = ("student", "issue_date","due_date", "return_date", "is_returned")

class BookCopySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = BookCopy
        fields = "__all__"
        read_only_fields = ("copy_uid", "qr_image", "created_at", "updated_at")

class IssueTransactionSerializer(serializers.ModelSerializer):
    copy_uid = serializers.CharField(source="copy.copy_uid", read_only=True)
    book_title = serializers.CharField(source="copy.book.title", read_only=True)
    student_name = serializers.CharField(source="student.username", read_only=True)
    issued_by_name = serializers.CharField(source="issued_by.username", read_only=True)
    returned_by_name = serializers.CharField(source="returned_by.username", read_only=True)

    class Meta:
        model = IssueTransaction
        fields = "__all__"
        read_only_fields = ("issued_at", "returned_at", "fine_amount", "status")

class BookRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = BookRequest
        fields = "__all__"
        read_only_fields = ("status", "requested_at", "processed_by", "processed_at")

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True, default="System")

    class Meta:
        model = AuditLog
        fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

class WaitlistSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Waitlist
        fields = "__all__"
        read_only_fields = ("student", "created_at")

class BookSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookSummary
        fields = "__all__"
        read_only_fields = ("generated_at",)

class BookDemandSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="requested_by.name", read_only=True)
    
    class Meta:
        model = BookDemand
        fields = "__all__"
        read_only_fields = ("requested_by", "request_count", "status", "created_at")