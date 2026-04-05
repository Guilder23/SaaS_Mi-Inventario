from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planes", "0002_seed_default_plans"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="permite_modo_oscuro",
            field=models.BooleanField(
                default=True,
                help_text="Permite usar el modo oscuro/claro en la interfaz.",
            ),
        ),
    ]
