import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0003_volunteer_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignment",
            name="covered_by",
            field=models.ForeignKey(
                blank=True,
                help_text="If declined, who has agreed to cover this instead.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="covering_for",
                to="scheduling.volunteer",
            ),
        ),
    ]