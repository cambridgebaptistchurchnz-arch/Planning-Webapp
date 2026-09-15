from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives


def send_assignment_email(assignment):
    """Email a volunteer about a single assignment, with their personal
    approve/decline link. Marks the assignment as notified."""

    respond_url = f"{settings.SITE_URL}/respond/{assignment.token}/"

    context = {
        "assignment": assignment,
        "respond_url": respond_url,
    }

    subject = f"Can you serve on {assignment.role} — {assignment.service_week}?"
    text_body = render_to_string("emails/assignment_email.txt", context)
    html_body = render_to_string("emails/assignment_email.html", context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[assignment.volunteer.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()

    assignment.notified_at = timezone.now()
    assignment.save(update_fields=["notified_at"])
