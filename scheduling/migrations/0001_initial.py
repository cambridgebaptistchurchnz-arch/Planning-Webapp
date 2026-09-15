import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="ServiceWeek",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(help_text="The Sunday (or service date) this roster is for.")),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Optional, e.g. 'Sunday AM' or 'Christmas Eve'.",
                        max_length=100,
                    ),
                ),
            ],
            options={"ordering": ["-date"], "unique_together": {("date", "label")}},
        ),
        migrations.CreateModel(
            name="Volunteer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=30)),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="Untick to hide this person from future scheduling without deleting their history.",
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("declined", "Declined")],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("notified_at", models.DateTimeField(blank=True, null=True)),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="scheduling.role",
                    ),
                ),
                (
                    "service_week",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="scheduling.serviceweek",
                    ),
                ),
                (
                    "volunteer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="scheduling.volunteer",
                    ),
                ),
            ],
            options={
                "ordering": ["service_week", "role", "volunteer"],
                "unique_together": {("volunteer", "role", "service_week")},
            },
        ),
    ]
