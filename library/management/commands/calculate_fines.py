import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from library.models import Issue

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Calculates fines linearly for overdue books and updates the Issue records. Can be safely run daily via Crontab."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # Filter: Only process issues that haven't been returned, and where today > due_date
        # Fine status must be UNPAID (we don't accrue fine if it's already marked paid)
        overdue_issues = Issue.objects.filter(
            is_returned=False,
            fine_status=Issue.STATUS_UNPAID,
            due_date__lt=today
        )

        FINE_PER_DAY = 5
        MAX_FINE = 500

        updated_count = 0
        
        for issue in overdue_issues:
            days_late = (today - issue.due_date).days
            
            if days_late > 0:
                calculated_fine = days_late * FINE_PER_DAY
                
                # Cap the maximum fine to 500
                if calculated_fine > MAX_FINE:
                    calculated_fine = MAX_FINE
                
                # Update only if fine changes to avoid unnecessary DB writes
                if issue.fine_amount != calculated_fine:
                    issue.fine_amount = calculated_fine
                    issue.save(update_fields=['fine_amount'])
                    updated_count += 1
                    logger.info(f"Updated Issue {issue.id} with fine ₹{calculated_fine}")

        self.stdout.write(self.style.SUCCESS(f"Successfully updated fines for {updated_count} overdue issues."))
