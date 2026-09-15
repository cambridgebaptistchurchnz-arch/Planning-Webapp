import uuid

from django.db import models


class Volunteer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(
        default=True,
        help_text="Untick to hide this person from future scheduling without deleting their history.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ServiceWeek(models.Model):
    date = models.DateField(help_text="The Sunday (or service date) this roster is for.")
    label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional, e.g. 'Sunday AM' or 'Christmas Eve'.",
    )

    class Meta:
        ordering = ["-date"]
        unique_together = ("date", "label")

    def __str__(self):
        return f"{self.date}" + (f" — {self.label}" if self.label else "")


class Assignment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"

    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, related_name="assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="assignments")
    service_week = models.ForeignKey(ServiceWeek, on_delete=models.CASCADE, related_name="assignments")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["service_week", "role", "volunteer"]
        unique_together = ("volunteer", "role", "service_week")

    def __str__(self):
        return f"{self.volunteer} — {self.role} ({self.service_week})"
