from django.core.management.base import BaseCommand, CommandError

from scheduling.emailing import send_assignment_email
from scheduling.models import Assignment, ServiceWeek


class Command(BaseCommand):
    help = "Emails every pending (not-yet-notified) volunteer assigned to a given service week."

    def add_arguments(self, parser):
        parser.add_argument(
            "--week",
            required=True,
            help="Date of the service week, e.g. 2026-09-20",
        )
        parser.add_argument(
            "--resend",
            action="store_true",
            help="Also re-email people who were already notified but haven't responded yet.",
        )

    def handle(self, *args, **options):
        try:
            week = ServiceWeek.objects.get(date=options["week"])
        except ServiceWeek.DoesNotExist as exc:
            raise CommandError(f"No ServiceWeek found for date {options['week']}") from exc

        assignments = Assignment.objects.filter(service_week=week, status=Assignment.Status.PENDING)
        if not options["resend"]:
            assignments = assignments.filter(notified_at__isnull=True)

        count = 0
        for assignment in assignments:
            send_assignment_email(assignment)
            count += 1
            self.stdout.write(f"Emailed {assignment.volunteer.name} ({assignment.role})")

        self.stdout.write(self.style.SUCCESS(f"Done. Sent {count} email(s) for {week}."))
