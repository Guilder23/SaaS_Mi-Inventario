from django.db import migrations


def seed_default_plans(apps, schema_editor):
    Plan = apps.get_model("planes", "Plan")
    PlanRolLimite = apps.get_model("planes", "PlanRolLimite")

    # No imponemos límites por defecto para no bloquear a empresas existentes.
    defaults = [
        ("basico", "Básico"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    ]

    roles = [
        "administrador",
        "almacen",
        "tienda",
        "deposito",
        "tienda_online",
    ]

    for codigo, nombre in defaults:
        plan, _created = Plan.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nombre": nombre,
                "activo": True,
                "max_productos": None,
                "max_usuarios_total": None,
            },
        )

        for rol in roles:
            PlanRolLimite.objects.get_or_create(plan=plan, rol=rol)


class Migration(migrations.Migration):

    dependencies = [
        ("planes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_default_plans, migrations.RunPython.noop),
    ]
