from django.db import migrations


def seed_default_empresa(apps, schema_editor):
    Empresa = apps.get_model('empresas', 'Empresa')

    empresa, _ = Empresa.objects.get_or_create(
        nombre='Empresa Principal',
        defaults={
            'activa': True,
            'plan': 'basico',
        },
    )

    modelos = [
        ('almacenes', 'Almacen'),
        ('tiendas', 'Tienda'),
        ('depositos', 'Deposito'),
        ('tiendas_virtuales', 'TiendaVirtual'),
        ('productos', 'Categoria'),
        ('productos', 'Contenedor'),
        ('productos', 'Producto'),
        ('productos', 'ProductoContenedor'),
        ('productos', 'HistorialProducto'),
        ('productos', 'ProductoDanado'),
        ('inventario', 'Inventario'),
        ('inventario', 'MovimientoInventario'),
        ('devoluciones', 'Devolucion'),
        ('ventas', 'Venta'),
        ('ventas', 'DetalleVenta'),
        ('ventas', 'AmortizacionCredito'),
        ('ventas', 'SolicitudAnulacionVenta'),
        ('pedidos', 'Pedido'),
        ('pedidos', 'DetallePedido'),
        ('traspasos', 'Traspaso'),
        ('traspasos', 'DetalleTraspaso'),
        ('vendedores', 'Vendedor'),
        ('notificaciones', 'Notificacion'),
    ]

    PerfilUsuario = apps.get_model('usuarios', 'PerfilUsuario')
    PerfilUsuario.objects.filter(empresa__isnull=True, usuario__is_superuser=False).update(empresa=empresa)

    for app_label, model_name in modelos:
        Model = apps.get_model(app_label, model_name)
        if 'empresa' in [field.name for field in Model._meta.fields]:
            Model.objects.filter(empresa__isnull=True).update(empresa=empresa)


def unseed_default_empresa(apps, schema_editor):
    Empresa = apps.get_model('empresas', 'Empresa')
    Empresa.objects.filter(nombre='Empresa Principal').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('empresas', '0001_initial'),
        ('usuarios', '0006_perfilusuario_empresa'),
        ('almacenes', '0003_almacen_empresa_alter_almacen_nombre_and_more'),
        ('tiendas', '0003_tienda_empresa_alter_tienda_nombre_and_more'),
        ('depositos', '0004_deposito_empresa_alter_deposito_nombre_and_more'),
        ('tiendas_virtuales', '0002_tiendavirtual_empresa_alter_tiendavirtual_codigo_and_more'),
        ('productos', '0012_categoria_empresa_contenedor_empresa_and_more'),
        ('inventario', '0002_inventario_empresa_movimientoinventario_empresa'),
        ('devoluciones', '0002_devolucion_empresa'),
        ('ventas', '0006_amortizacioncredito_empresa_detalleventa_empresa_and_more'),
        ('pedidos', '0002_detallepedido_empresa_pedido_empresa'),
        ('traspasos', '0003_detalletraspaso_empresa_traspaso_empresa'),
        ('vendedores', '0002_vendedor_empresa_alter_vendedor_cedula_and_more'),
        ('notificaciones', '0003_notificacion_empresa'),
    ]

    operations = [
        migrations.RunPython(seed_default_empresa, unseed_default_empresa),
    ]
