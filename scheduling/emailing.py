import requests
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from .models import EmailTemplate


class _SafePlaceholders(dict):
    """Leaves unknown {placeholders} untouched instead of raising an error,
    so a typo'd placeholder in a staff-edited template doesn't crash sending."""

    def __missing__(self, key):
        return "{" + key + "}"


def render_placeholders(template_string, context):
    return template_string.format_map(_SafePlaceholders(context))


def send_assignment_email(assignment):
    """Email a volunteer about a single assignment, with their personal
    approve/decline link, via the Resend API. Marks the assignment as
    notified on success. Subject and message wording come from the
    staff-editable EmailTemplate."""

    site_url = settings.SITE_URL.rstrip("/")
    respond_url = f"{site_url}/respond/{assignment.token}/"

    placeholder_values = {
        "volunteer_name": assignment.volunteer.name,
        "role": str(assignment.role),
        "service_week": str(assignment.service_week),
        "respond_url": respond_url,
    }

    template = EmailTemplate.get_solo()
    subject = render_placeholders(template.subject, placeholder_values)
    custom_body = render_placeholders(template.body, placeholder_values)

    context = {
        "assignment": assignment,
        "respond_url": respond_url,
        "custom_body": custom_body,
    }

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