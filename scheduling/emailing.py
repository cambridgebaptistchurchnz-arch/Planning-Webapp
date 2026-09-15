import requests
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone


def send_assignment_email(assignment):
    """Email a volunteer about a single assignment, with their personal
    approve/decline link, via the Resend API. Marks the assignment as
    notified on success."""

    site_url = settings.SITE_URL.rstrip("/")
    respond_url = f"{site_url}/respond/{assignment.token}/"

    context = {
        "assignment": assignment,
        "respond_url": respond_url,
    }

    subject = f"Can you serve on {assignment.role} - {assignment.service_week}?"
    text_body = render_to_string("emails/assignment_email.txt", context)
    html_body = render_to_string("emails/assignment_email.html", context)

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [assignment.volunteer.email],
            "subject": subject,
            "text": text_body,
            "html": html_body,
        },
        timeout=15,
    )
    response.raise_for_status()

    assignment.notified_at = timezone.now()
    assignment.save(update_fields=["notified_at"])