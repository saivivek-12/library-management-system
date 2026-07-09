import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from library.models import Issue

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Finds overdue issues and emails students a reminder. Can be safely run daily via Crontab."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # We only send reminders for issues that are NOT returned and OVERDUE.
        overdue_issues = Issue.objects.filter(
            is_returned=False,
            due_date__lt=today
        ).select_related('student', 'book')
        
        emails_sent = 0
        failed_emails = 0

        for issue in overdue_issues:
            student = issue.student
            book = issue.book
            
            days_late = (today - issue.due_date).days
            
            subject = f"[Library Reminder] Overdue Book: {book.title}"
            message = (
                f"Hello {student.name},\n\n"
                f"This is a reminder that the book '{book.title}' was due on {issue.due_date}.\n"
                f"It is currently {days_late} days late. "
            )
            
            if issue.fine_amount > 0:
                message += f"Your current accumulated fine is ₹{issue.fine_amount}.\n"
                
            message += "\nPlease return the book as soon as possible to avoid further fines.\n\nThank you,\nLibrary Administration"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [student.email],
                    fail_silently=False,
                )
                emails_sent += 1
                logger.info(f"Sent reminder email to {student.email} for Issue {issue.id}")
            except Exception as e:
                failed_emails += 1
                logger.error(f"Failed to send email to {student.email} for Issue {issue.id}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Successfully sent {emails_sent} reminders. {failed_emails} failed."))
