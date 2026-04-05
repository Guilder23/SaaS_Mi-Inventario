from django.db import migrations


def _drop_stock_column(apps, schema_editor):
    vendor = schema_editor.connection.vendor

    if vendor == 'postgresql':
        schema_editor.execute('ALTER TABLE productos_producto DROP COLUMN IF EXISTS stock;')
        return

    # SQLite:
    # - No soporta "IF EXISTS" en este contexto.
    # - "DROP COLUMN" depende de la versión de SQLite.
    # Para despliegues con SQLite, si no se puede eliminar la columna, no es crítico;
    # Django ignora columnas extras no mapeadas en el modelo.
    try:
        schema_editor.execute('ALTER TABLE productos_producto DROP COLUMN stock;')
    except Exception:
        return


def _add_stock_column_reverse(apps, schema_editor):
    vendor = schema_editor.connection.vendor

    if vendor == 'postgresql':
        schema_editor.execute('ALTER TABLE productos_producto ADD COLUMN IF NOT EXISTS stock INTEGER DEFAULT 0;')
        return

    try:
        schema_editor.execute('ALTER TABLE productos_producto ADD COLUMN stock INTEGER DEFAULT 0;')
    except Exception:
        return


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0008_remove_contenedor_stock_remove_producto_contenedor_and_more'),
    ]

    operations = [
        migrations.RunPython(_drop_stock_column, _add_stock_column_reverse),
    ]
