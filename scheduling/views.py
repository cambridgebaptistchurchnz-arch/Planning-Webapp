from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Assignment


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
