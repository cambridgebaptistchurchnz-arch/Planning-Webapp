from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
import json
import requests

from .emailing import send_assignment_email
from .forms import RoleForm, ServiceItemForm, ServiceWeekForm, StaffUserForm, VolunteerForm
from .models import Assignment, Role, ServiceWeek, Volunteer

User = get_user_model()


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
                item.order = week.order_of_service.count()
                item.save()
                messages.success(request, f"Added {item.title} to the order of service.")
            return redirect("service_week_detail", pk=pk)

        if "assign_volunteer" in request.POST:
            role = get_object_or_404(Role, pk=request.POST.get("role_id"))
            volunteer = get_object_or_404(Volunteer, pk=request.POST.get("volunteer_id"))
            assignment, created = Assignment.objects.get_or_create(
                service_week=week, role=role, volunteer=volunteer
            )
            if created:
                messages.success(request, f"Assigned {volunteer} to {role}.")
            else:
                messages.info(request, f"{volunteer} is already assigned to {role} this week.")
            return redirect("service_week_detail", pk=pk)

    items = week.order_of_service.all().order_by("order")
    assignments = week.assignments.select_related("role", "volunteer").order_by("role__name")

    item_form = ServiceItemForm()

    roles_with_eligible = []
    for role in Role.objects.all().order_by("name"):
        eligible = role.volunteers.filter(active=True).order_by("name")
        assigned_for_role = [a for a in assignments if a.role_id == role.id]
        roles_with_eligible.append((role, eligible, assigned_for_role))

    return render(
        request,
        "scheduling/service_week_detail.html",
        {
            "week": week,
            "items": items,
            "assignments": assignments,
            "item_form": item_form,
            "roles_with_eligible": roles_with_eligible,
        },
    )


@staff_member_required
def reorder_service_items(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    week = get_object_or_404(ServiceWeek, pk=pk)

    try:
        data = json.loads(request.body)
        item_ids = data.get("order", [])
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid payload"}, status=400)

    items_by_id = {item.id: item for item in week.order_of_service.all()}
    for index, item_id in enumerate(item_ids):
        item = items_by_id.get(int(item_id))
        if item:
            item.order = index
            item.save(update_fields=["order"])

    return JsonResponse({"status": "ok"})


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


@staff_member_required
def volunteer_list(request):
    volunteers = Volunteer.objects.all().order_by("name")
    return render(request, "scheduling/volunteer_list.html", {"volunteers": volunteers})


@staff_member_required
def volunteer_edit(request, pk=None):
    volunteer = get_object_or_404(Volunteer, pk=pk) if pk else None
    if request.method == "POST":
        form = VolunteerForm(request.POST, instance=volunteer)
        if form.is_valid():
            form.save()
            messages.success(request, "Saved volunteer.")
            return redirect("volunteer_list")
    else:
        form = VolunteerForm(instance=volunteer)
    return render(request, "scheduling/volunteer_form.html", {"form": form, "volunteer": volunteer})


@staff_member_required
def volunteer_delete(request, pk):
    volunteer = get_object_or_404(Volunteer, pk=pk)
    volunteer.delete()
    messages.success(request, "Removed volunteer.")
    return redirect("volunteer_list")


@staff_member_required
def role_list(request):
    roles = Role.objects.all().order_by("name")
    return render(request, "scheduling/role_list.html", {"roles": roles})


@staff_member_required
def role_edit(request, pk=None):
    role = get_object_or_404(Role, pk=pk) if pk else None
    if request.method == "POST":
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Saved role.")
            return redirect("role_list")
    else:
        form = RoleForm(instance=role)
    return render(request, "scheduling/role_form.html", {"form": form, "role": role})


@staff_member_required
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    role.delete()
    messages.success(request, "Removed role.")
    return redirect("role_list")


@staff_member_required
def user_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to manage logins.")
    users = User.objects.all().order_by("username")
    return render(request, "scheduling/user_list.html", {"users": users})


@staff_member_required
def user_edit(request, pk=None):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to manage logins.")

    staff_user = get_object_or_404(User, pk=pk) if pk else None

    if request.method == "POST":
        form = StaffUserForm(request.POST, instance=staff_user)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            if not staff_user and not password:
                form.add_error("password", "A password is required for a new login.")
            else:
                user_obj = form.save(commit=False)
                if password:
                    user_obj.set_password(password)
                user_obj.save()
                messages.success(request, "Saved login.")
                return redirect("user_list")
    else:
        form = StaffUserForm(instance=staff_user)

    return render(request, "scheduling/user_form.html", {"form": form, "staff_user": staff_user})


@staff_member_required
def user_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to manage logins.")

    staff_user = get_object_or_404(User, pk=pk)
    if staff_user.pk == request.user.pk:
        messages.error(request, "You can't remove your own login while logged in as it.")
        return redirect("user_list")

    staff_user.delete()
    messages.success(request, "Removed login.")
    return redirect("user_list")