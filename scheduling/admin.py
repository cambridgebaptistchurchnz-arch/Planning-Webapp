from django.contrib import admin, messages
from django.utils.html import format_html
import requests

from .emailing import send_assignment_email
from .models import Assignment, Role, ServiceWeek, Volunteer

admin.site.site_header = "Church Roster"
admin.site.site_title = "Church Roster"
admin.site.index_title = "Volunteer Scheduling"


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "active")
    list_filter = ("active",)
    search_fields = ("name", "email")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(ServiceWeek)
class ServiceWeekAdmin(admin.ModelAdmin):
    list_display = ("date", "label")
    list_filter = ("date",)
    ordering = ("-date",)
    search_fields = ("label",)


def send_selected_assignment_emails(modeladmin, request, queryset):
    sent = 0
    for assignment in queryset:
        try:
            send_assignment_email(assignment)
            sent += 1
        except requests.exceptions.HTTPError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            messages.error(
                request,
                f"Failed to email {assignment.volunteer.name}: {detail}",
            )
        except Exception as exc:  # noqa: BLE001 - surface any other failure to the admin UI
            messages.error(request, f"Failed to email {assignment.volunteer.name}: {exc}")

    if sent:
        messages.success(request, f"Sent {sent} email(s).")


send_selected_assignment_emails.short_description = "Email selected volunteers their assignment"


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    # This is the screen office staff will live in day-to-day: it shows,
    # at a glance, who is assigned to what and whether they've responded.
    list_display = (
        "service_week",
        "role",
        "volunteer",
        "status_badge",
        "notified_at",
        "responded_at",
    )
    list_filter = ("status", "service_week", "role")
    search_fields = ("volunteer__name", "role__name")
    autocomplete_fields = ("volunteer", "role", "service_week")
    actions = [send_selected_assignment_emails]

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        return format_html(
            '<span class="status-badge status-badge--{}">{}</span>',
            obj.status,
            obj.get_status_display(),
        )