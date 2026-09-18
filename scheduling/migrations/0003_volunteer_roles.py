from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0002_serviceitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteer",
            name="roles",
            field=models.ManyToManyField(
                blank=True,
                help_text="Which roles this person can be scheduled for.",
                related_name="volunteers",
                to="scheduling.role",
            ),
        ),
    ]