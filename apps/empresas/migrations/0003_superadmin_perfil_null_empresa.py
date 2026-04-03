from django.db import migrations


def clear_superadmin_empresa(apps, schema_editor):
    PerfilUsuario = apps.get_model('usuarios', 'PerfilUsuario')
    PerfilUsuario.objects.filter(usuario__is_superuser=True).update(empresa=None)


def restore_superadmin_empresa(apps, schema_editor):
    # No-op: evitar reasignar empresa en reversa
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('empresas', '0002_seed_default_empresa'),
    ]

    operations = [
        migrations.RunPython(clear_superadmin_empresa, restore_superadmin_empresa),
    ]
