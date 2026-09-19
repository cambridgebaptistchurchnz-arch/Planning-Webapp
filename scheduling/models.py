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
    roles = models.ManyToManyField(
        "Role",
        blank=True,
        related_name="volunteers",
        help_text="Which roles this person can be scheduled for.",
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
    covered_by = models.ForeignKey(
        Volunteer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="covering_for",
        help_text="If declined, who has agreed to cover this instead.",
    )

    class Meta:
        ordering = ["service_week", "role", "volunteer"]
        unique_together = ("volunteer", "role", "service_week")

    def __str__(self):
        return f"{self.volunteer} — {self.role} ({self.service_week})"


class ServiceItem(models.Model):
    class ItemType(models.TextChoices):
        SONG = "song", "Song"
        READING = "reading", "Scripture Reading"
        SERMON = "sermon", "Sermon"
        PRAYER = "prayer", "Prayer"
        ANNOUNCEMENT = "announcement", "Announcement"
        OFFERING = "offering", "Offering"
        COMMUNION = "communion", "Communion"
        OTHER = "other", "Other"

    service_week = models.ForeignKey(ServiceWeek, on_delete=models.CASCADE, related_name="order_of_service")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")
    item_type = models.CharField(max_length=20, choices=ItemType.choices, default=ItemType.OTHER)
    title = models.CharField(max_length=200, help_text="e.g. song title, sermon topic, announcement subject.")
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Lyrics reference, speaker name, key, anything the team needs.")

    class Meta:
        ordering = ["service_week", "order"]

    def __str__(self):
        return f"{self.get_item_type_display()}: {self.title}"