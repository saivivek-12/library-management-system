from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Waitlist, Issue, Notification, BookCopy, IssueTransaction
from .utils import create_audit_log

def auto_issue_from_waitlist(book, request_user):
    """
    Safely issues available copies of a book to waitlisted students in FIFO order.
    Loops safely until No physical copies OR No waitlist.
    Must be called within an atomic transaction or manages its own.
    Returns the number of books issued.
    """
    issued_count = 0
    with transaction.atomic():
        # Important: We loop based on available physical copies
        while True:
            # 1. Check for physical copy
            available_copy = BookCopy.objects.filter(book=book, status=BookCopy.STATUS_AVAILABLE).first()
            if not available_copy:
                break
            
            # 2. Check for waitlister
            waitlister = Waitlist.objects.filter(book=book).select_related('student__user').first()
            if not waitlister:
                break
            
            # 3. Issue the book
            due_date = timezone.now().date() + timedelta(days=14)
            
            # Physical issue
            available_copy.status = BookCopy.STATUS_ISSUED
            available_copy.save(update_fields=["status"])
            
            # Create Transaction
            IssueTransaction.objects.create(
                copy=available_copy,
                student=waitlister.student.user,
                issued_by=request_user,
                due_date=due_date,
                status=IssueTransaction.STATUS_ISSUED
            )

            # Backwards compatibility: Create legacy Issue
            Issue.objects.create(
                student=waitlister.student, 
                book=book,
                due_date=due_date
            )
            
            # Update book count
            book.available_copies = BookCopy.objects.filter(book=book, status=BookCopy.STATUS_AVAILABLE).count()
            book.save(update_fields=["available_copies"])
            
            # Notify
            Notification.objects.create(
                user=waitlister.student.user,
                message=f"The book '{book.title}' you waitlisted is now available and has been automatically issued to you! Due date: {due_date}"
            )
            
            # Audit log
            create_audit_log(request_user, "Auto-issue from waitlist", "Waitlist", book.id, f"Automatically issued {book.title} (Copy: {available_copy.copy_uid}) to {waitlister.student.roll_no}")
            
            # Remove from waitlist
            waitlister.delete()
            issued_count += 1
            
    return issued_count
