from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0004_assignment_covered_by"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "subject",
                    models.CharField(
                        default="Can you serve on {role} - {service_week}?",
                        help_text="Placeholders: {volunteer_name} {role} {service_week} {respond_url}",
                        max_length=200,
                    ),
                ),
                (
                    "body",
                    models.TextField(
                        default=(
                            "Hi {volunteer_name},\n\n"
                            "You've been scheduled to serve as {role} on {service_week}. "
                            "Please confirm whether you're able to make it using the button below."
                        ),
                        help_text="Placeholders: {volunteer_name} {role} {service_week} {respond_url}",
                    ),
                ),
            ],
        ),
    ]