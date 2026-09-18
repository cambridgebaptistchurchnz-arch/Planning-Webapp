from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
import requests

from .emailing import send_assignment_email
from .forms import AssignmentForm, ServiceItemForm, ServiceWeekForm
from .models import Assignment, ServiceWeek


def respond_to_assignment(request, token):
    assignment = get_object_or_404(Assignment, token=token)

    if request.method == "POST":
        action = request.POST.get("action")
        if action in ("approve", "decline"):
            assignment.status = (
                Assignment.Status.APPROVED if action == "approve" else Assignment.Status.DECLINED
            )
            assignment.responded_at = timezone.now()
            assignment.save(update_fields=["status", "responded_at"])

    return render(request, "scheduling/respond.html", {"assignment": assignment})


@staff_member_required
def dashboard(request):
    if request.method == "POST":
        form = ServiceWeekForm(request.POST)
        if form.is_valid():
            week = form.save()
            messages.success(request, f"Created {week}.")
            return redirect("service_week_detail", pk=week.pk)
    else:
        form = ServiceWeekForm()

    weeks = ServiceWeek.objects.all().order_by("-date")
    return render(request, "scheduling/dashboard.html", {"weeks": weeks, "form": form})


@staff_member_required
def service_week_detail(request, pk):
    week = get_object_or_404(ServiceWeek, pk=pk)

    if request.method == "POST":
        if "add_item" in request.POST:
            item_form = ServiceItemForm(request.POST)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.service_week = week
                item.save()
                messages.success(request, f"Added {item.title} to the order of service.")
            return redirect("service_week_detail", pk=pk)

        if "add_assignment" in request.POST:
            assignment_form = AssignmentForm(request.POST)
            if assignment_form.is_valid():
                assignment = assignment_form.save(commit=False)
                assignment.service_week = week
                assignment.save()
                messages.success(request, f"Assigned {assignment.volunteer} to {assignment.role}.")
            return redirect("service_week_detail", pk=pk)

    items = week.order_of_service.all().order_by("order")
    assignments = week.assignments.select_related("role", "volunteer").order_by("role__name")

    item_form = ServiceItemForm()
    assignment_form = AssignmentForm()

    return render(
        request,
        "scheduling/service_week_detail.html",
        {
            "week": week,
            "items": items,
            "assignments": assignments,
            "item_form": item_form,
            "assignment_form": assignment_form,
        },
    )


@staff_member_required
def delete_service_item(request, pk, item_id):
    item = get_object_or_404(week_items_qs(pk), pk=item_id)
    item.delete()
    messages.success(request, "Removed item.")
    return redirect("service_week_detail", pk=pk)


@staff_member_required
def delete_assignment(request, pk, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id, service_week_id=pk)
    assignment.delete()
    messages.success(request, "Removed assignment.")
    return redirect("service_week_detail", pk=pk)


@staff_member_required
def email_assignment(request, pk, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id, service_week_id=pk)
    try:
        send_assignment_email(assignment)
        messages.success(request, f"Emailed {assignment.volunteer.name}.")
    except requests.exceptions.HTTPError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        messages.error(request, f"Failed to email {assignment.volunteer.name}: {detail}")
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Failed to email {assignment.volunteer.name}: {exc}")
    return redirect("service_week_detail", pk=pk)


@staff_member_required
def email_all_pending(request, pk):
    week = get_object_or_404(ServiceWeek, pk=pk)
    pending = week.assignments.filter(status=Assignment.Status.PENDING)
    sent = 0
    for assignment in pending:
        try:
            send_assignment_email(assignment)
            sent += 1
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Failed to email {assignment.volunteer.name}: {exc}")
    if sent:
        messages.success(request, f"Sent {sent} email(s).")
    return redirect("service_week_detail", pk=pk)


def week_items_qs(pk):
    from .models import ServiceItem

    return ServiceItem.objects.filter(service_week_id=pk)