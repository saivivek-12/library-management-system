from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import uuid
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
import re

def sanitize_filename(name):
    """Sanitize a string to be used as a filename."""
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

class Author(models.Model):
    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100, null=True, blank=True)
    target_id = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.user}: {self.message[:20]}..."


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=120)
    roll_no = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, default="CSE")
    year = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    ROLE_STUDENT = 'STUDENT'
    ROLE_LIBRARIAN = 'LIBRARIAN'
    ROLE_SUPER_ADMIN = 'SUPER_ADMIN'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_LIBRARIAN, 'Librarian'),
        (ROLE_SUPER_ADMIN, 'Super Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)

    # login tracking
    LOGIN_METHOD_PASSWORD = 'PASSWORD'
    LOGIN_METHOD_QR = 'QR'
    LOGIN_METHOD_ID_CARD = 'ID_CARD'
    LOGIN_METHOD_CHOICES = [
        (LOGIN_METHOD_PASSWORD, 'Password'),
        (LOGIN_METHOD_QR, 'QR Code'),
        (LOGIN_METHOD_ID_CARD, 'ID Card'),
    ]
    login_method = models.CharField(max_length=20, choices=LOGIN_METHOD_CHOICES, default=LOGIN_METHOD_PASSWORD)
    last_id_card_login = models.DateTimeField(null=True, blank=True)

    qr_uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    qr_image = models.ImageField(upload_to='user_qr/', null=True, blank=True)

    def save(self, *args, **kwargs):
        generate_qr = False
        if not self.pk or not self.qr_image:
            generate_qr = True

        super().save(*args, **kwargs)

        if generate_qr and self.roll_no:
            try:
                # Generate Code 128 Barcode for Student Roll Number
                COD128 = barcode.get_barcode_class('code128')
                writer = ImageWriter()
                # Set fixed height for barcodes to look consistent
                writer.set_options({
                    'module_height': 5.0,
                    'font_size': 0, # Hide text as it's often on the ID already
                    'text_distance': 0,
                })
                
                # Data for student barcode is just their roll_no
                barcode_instance = COD128(self.roll_no, writer=writer)
                
                buffer = BytesIO()
                barcode_instance.write(buffer)
                
                safe_name = sanitize_filename(self.name)
                filename = f"user_barcode_{safe_name}_{self.roll_no}.png"
                self.qr_image.save(filename, File(buffer), save=False)
                Student.objects.filter(pk=self.pk).update(qr_image=self.qr_image)
            except Exception:
                pass

    def __str__(self):
        return f"{self.roll_no} - {self.name}"


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    category = models.CharField(max_length=120)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    qr_uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    qr_image = models.ImageField(upload_to='book_qr/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Calculate availability on save if not provided
        if is_new and self.available_copies is None:
            self.available_copies = self.total_copies
            
        generate_qr = False
        if not self.pk or not self.qr_image:
            generate_qr = True

        super().save(*args, **kwargs)

        if generate_qr:
            try:
                # Generate Code 128 Barcode for Book
                COD128 = barcode.get_barcode_class('code128')
                writer = ImageWriter()
                writer.set_options({'module_height': 5.0, 'font_size': 0})
                
                # Using BOOK prefix for identification
                barcode_instance = COD128(f"BOOK:{str(self.qr_uid)[:12]}", writer=writer)
                
                buffer = BytesIO()
                barcode_instance.write(buffer)
                
                safe_title = sanitize_filename(self.title)
                filename = f"book_barcode_{safe_title}_{str(self.qr_uid)[:8]}.png"
                self.qr_image.save(filename, File(buffer), save=False)
                Book.objects.filter(pk=self.pk).update(qr_image=self.qr_image)
            except Exception:
                pass

        # After saving, ensure BookCopies match total_copies
        from .models import BookCopy
        current_copies = BookCopy.objects.filter(book=self).count()
        if current_copies < self.total_copies:
            needed = self.total_copies - current_copies
            for _ in range(needed):
                BookCopy.objects.create(book=self)
        elif current_copies > self.total_copies:
            # We need to remove copies safely (only available ones)
            excess = current_copies - self.total_copies
            available_to_delete = BookCopy.objects.filter(book=self, status=BookCopy.STATUS_AVAILABLE)[:excess]
            for copy in available_to_delete:
                copy.delete()

class BookSummary(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='summary')
    short_description = models.TextField()
    key_points = models.JSONField()  # Stores 5 bullet points
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for {self.book.title}"

class BookDemand(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    requested_by = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_demands')
    request_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author} ({self.request_count} requests)"

class BookCopy(models.Model):
    STATUS_AVAILABLE = 'AVAILABLE'
    STATUS_ISSUED = 'ISSUED'
    STATUS_LOST = 'LOST'
    STATUS_DAMAGED = 'DAMAGED'
    
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_ISSUED, 'Issued'),
        (STATUS_LOST, 'Lost'),
        (STATUS_DAMAGED, 'Damaged'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    copy_uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        generate_qr = False
        if not self.pk or not self.qr_image:
            generate_qr = True
            
        super().save(*args, **kwargs)

        if generate_qr:
            # Generate Code 128 Barcode for BookCopy
            COD128 = barcode.get_barcode_class('code128')
            writer = ImageWriter()
            writer.set_options({'module_height': 5.0, 'font_size': 0})
            
            # Using COPY prefix for identification
            barcode_instance = COD128(f"COPY:{str(self.copy_uid)[:12]}", writer=writer)
            
            buffer = BytesIO()
            barcode_instance.write(buffer)
            
            safe_title = sanitize_filename(self.book.title)
            filename = f"copy_barcode_{safe_title}_{str(self.copy_uid)[:8]}.png"
            self.qr_image.save(filename, File(buffer), save=False)
            # Update the image field without triggering infinite save loop
            BookCopy.objects.filter(pk=self.pk).update(qr_image=self.qr_image)

    def __str__(self):
        return f"{self.book.title} - Copy {str(self.copy_uid)[:8]}"


class IssueTransaction(models.Model):
    STATUS_ISSUED = 'ISSUED'
    STATUS_RETURNED = 'RETURNED'
    
    STATUS_CHOICES = [
        (STATUS_ISSUED, 'Issued'),
        (STATUS_RETURNED, 'Returned'),
    ]

    copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='transactions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_transactions')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_issues')
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    
    returned_at = models.DateTimeField(null=True, blank=True)
    returned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_returns')
    
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ISSUED)

    def __str__(self):
        return f"{self.student.username} - {self.copy.book.title} ({self.status})"



class Issue(models.Model):
    STATUS_UNPAID = 'UNPAID'
    STATUS_PAID = 'PAID'
    FINE_CHOICES = [(STATUS_UNPAID, 'Unpaid'), (STATUS_PAID, 'Paid')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="issues")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issues")
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)   # allow auto-fill
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    
    # New Fine Tracking Fields
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_status = models.CharField(max_length=10, choices=FINE_CHOICES, default=STATUS_UNPAID)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.roll_no} -> {self.book.title}"

    def save(self, *args, **kwargs):
        # Auto set due_date to 14 days from issue_date if not provided
        if not self.due_date:
            # issue_date may not exist before first save; use today
            base = self.issue_date or timezone.now().date()
            self.due_date = base + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.is_returned or self.return_date:
            return False
        return timezone.now().date() > self.due_date

    # Now returning the stored fine_amount rather than a dynamically calculated one
    # Note: Dynamic calculation is handled by the automation cron task.
    @property
    def fine(self):
        return self.fine_amount
    

class BookRequest(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_WAITLISTED = "WAITLISTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_WAITLISTED, "Waitlisted"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="requests")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="requests")
    requested_at = models.DateTimeField(auto_now_add=True)

    # optional fields
    note = models.CharField(max_length=255, blank=True, default="")
    due_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_comment = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.student.roll_no} -> {self.book.title} ({self.status})"

class Waitlist(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="waitlists")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="waitlists")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'book')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.student.roll_no} waiting for {self.book.title}"