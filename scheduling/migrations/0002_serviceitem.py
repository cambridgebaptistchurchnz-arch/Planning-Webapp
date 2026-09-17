import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")),
                (
                    "item_type",
                    models.CharField(
                        choices=[
                            ("song", "Song"),
                            ("reading", "Scripture Reading"),
                            ("sermon", "Sermon"),
                            ("prayer", "Prayer"),
                            ("announcement", "Announcement"),
                            ("offering", "Offering"),
                            ("communion", "Communion"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=20,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="e.g. song title, sermon topic, announcement subject.",
                        max_length=200,
                    ),
                ),
                ("duration_minutes", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Lyrics reference, speaker name, key, anything the team needs.",
                    ),
                ),
                (
                    "service_week",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_of_service",
                        to="scheduling.serviceweek",
                    ),
                ),
            ],
            options={
                "ordering": ["service_week", "order"],
            },
        ),
    ]