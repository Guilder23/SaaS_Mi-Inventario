from django.db import models
from django.contrib.auth.models import User

from apps.core.tenancy import EmpresaOwnedModel


class Categoria(EmpresaOwnedModel):
    """Modelo de Categoría de productos"""
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='categorias')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='categorias_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'nombre'], name='uniq_categoria_empresa_nombre'),
        ]

    def __str__(self):
        return self.nombre


class Contenedor(EmpresaOwnedModel):
    """Modelo de Contenedor de productos"""
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='contenedores')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    proveedor = models.CharField(max_length=150)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contenedores_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Contenedor'
        verbose_name_plural = 'Contenedores'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'nombre'], name='uniq_contenedor_empresa_nombre'),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.proveedor}"
    
    @property
    def stock_total(self):
        """Calcula el stock total que trae este contenedor"""
        return self.productos_contenedores.aggregate(
            total=models.Sum('cantidad')
        )['total'] or 0
    
    @property
    def total_recibido(self):
        """Calcula el total de cantidad recibida de este contenedor"""
        return self.productos_contenedores.aggregate(
            total=models.Sum('cantidad_recibida')
        )['total'] or 0


class ProductoContenedor(EmpresaOwnedModel):
    """Modelo intermedio para manejar la relación entre Productos y Contenedores
    Un producto puede llegar en múltiples contenedores, cada uno con su propia cantidad"""
    
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='productos_contenedores')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, 
                                related_name='productos_contenedores',
                                verbose_name='Producto')
    contenedor = models.ForeignKey('Contenedor', on_delete=models.CASCADE,
                                  related_name='productos_contenedores',
                                  verbose_name='Contenedor')
    cantidad_recibida = models.IntegerField(default=0, verbose_name='Cantidad recibida',
                                  help_text='Cantidad original que llegó en este contenedor (registro histórico)')
    cantidad = models.IntegerField(default=0, verbose_name='Cantidad disponible',
                                  help_text='Cantidad actualmente disponible en este contenedor')
    
    # Metadata
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='productos_contenedores_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto en Contenedor'
        verbose_name_plural = 'Productos en Contenedores'
        unique_together = ('producto', 'contenedor')  # Un producto solo una vez por contenedor
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.contenedor.nombre} ({self.cantidad} unidades)"
    
    def save(self, *args, **kwargs):
        """Guarda el ProductoContenedor"""
        if not self.empresa_id:
            if self.producto_id:
                self.empresa = self.producto.empresa
            elif self.contenedor_id:
                self.empresa = self.contenedor.empresa
        super().save(*args, **kwargs)


class Producto(EmpresaOwnedModel):
    """Modelo de Producto"""
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='productos')
    codigo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    descripcion = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='productos/', blank=True, null=True)
    unidades_por_caja = models.IntegerField(default=1)
    
    # Precios (administrador puede configurar todos)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_caja = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_mayor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_unidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    poliza = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    gastos = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    
    # Control de stock (se calcula automáticamente desde ProductoContenedor)
    stock_critico = models.IntegerField(default=10)
    stock_bajo = models.IntegerField(default=30)
    
    # Auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='productos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'codigo'], name='uniq_producto_empresa_codigo'),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def stock(self):
        """Calcula el stock total sumando todos los productos en contenedores"""
        return self.productos_contenedores.aggregate(
            total_stock=models.Sum('cantidad')
        )['total_stock'] or 0
    
    def obtener_stock_por_contenedor(self):
        """Retorna un diccionario con el stock del producto en cada contenedor"""
        return self.productos_contenedores.values(
            'contenedor__nombre', 'cantidad', 'id'
        ).order_by('contenedor__nombre')
    
    def reducir_stock(self, cantidad, usuario=None):
        """
        Reduce el stock del producto restando de los ProductoContenedor disponibles.
        Retorna True si se pudo reducir completamente, False en caso contrario.
        """
        if cantidad <= 0:
            return False
        
        # Verificar que hay stock suficiente
        if self.stock < cantidad:
            return False
        
        # Restar de los contenedores con stock disponible (FIFO - primeros en entrar)
        cantidad_restante = cantidad
        contenedores_con_stock = self.productos_contenedores.filter(
            cantidad__gt=0
        ).order_by('fecha_creacion')
        
        for pc in contenedores_con_stock:
            if cantidad_restante <= 0:
                break
            
            if pc.cantidad >= cantidad_restante:
                # Este contenedor tiene suficiente
                pc.cantidad -= cantidad_restante
                cantidad_restante = 0
                pc.save(update_fields=['cantidad', 'fecha_actualizacion'])
            else:
                # Este contenedor no tiene suficiente, usar todo y continuar
                cantidad_restante -= pc.cantidad
                pc.cantidad = 0
                pc.save(update_fields=['cantidad', 'fecha_actualizacion'])
        
        return cantidad_restante == 0
    
    def aumentar_stock(self, cantidad, usuario=None, contenedor=None):
        """
        Aumenta el stock del producto agregando a un ProductoContenedor.
        Si no se especifica contenedor, usa el más reciente o crea uno genérico.
        Retorna True si se pudo aumentar, False en caso contrario.
        """
        if cantidad <= 0:
            return False
        
        # Si no se especifica contenedor, usar el más reciente o crear uno genérico
        if contenedor is None:
            # Buscar el contenedor más reciente de este producto
            ultimo_pc = self.productos_contenedores.order_by('-fecha_creacion').first()
            if ultimo_pc:
                ultimo_pc.cantidad += cantidad
                ultimo_pc.save(update_fields=['cantidad', 'fecha_actualizacion'])
                return True
            else:
                # No hay contenedores, buscar/crear uno genérico llamado "Stock General"
                from django.contrib.auth.models import User
                contenedor_general, creado = Contenedor.objects.get_or_create(
                    nombre='Stock General',
                    defaults={
                        'proveedor': 'Sistema',
                        'creado_por': usuario,
                        'activo': True
                    }
                )
                ProductoContenedor.objects.create(
                    producto=self,
                    contenedor=contenedor_general,
                    cantidad_recibida=cantidad,
                    cantidad=cantidad,
                    creado_por=usuario
                )
                return True
        else:
            # Usar el contenedor especificado
            pc, creado = ProductoContenedor.objects.get_or_create(
                producto=self,
                contenedor=contenedor,
                defaults={'cantidad_recibida': cantidad, 'cantidad': cantidad, 'creado_por': usuario}
            )
            if not creado:
                pc.cantidad_recibida += cantidad
                pc.cantidad += cantidad
                pc.save(update_fields=['cantidad_recibida', 'cantidad', 'fecha_actualizacion'])
            return True


class HistorialProducto(EmpresaOwnedModel):
    """Historial de cambios en productos"""
    ACCIONES = (
        ('creacion', 'Creación'),
        ('edicion', 'Edición'),
        ('eliminacion', 'Eliminación'),
    )
    
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='historial_productos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='historial')
    accion = models.CharField(max_length=20, choices=ACCIONES)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    detalles = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Producto'
        verbose_name_plural = 'Historiales de Productos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.producto.codigo} - {self.get_accion_display()} - {self.fecha}"

    def save(self, *args, **kwargs):
        if not self.empresa_id and self.producto_id:
            self.empresa = self.producto.empresa
        super().save(*args, **kwargs)


class ProductoDanado(EmpresaOwnedModel):
    """Registro de productos dañados"""
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('parcial', 'Parcial'),
        ('cerrado', 'Cerrado'),
    )

    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='productos_danados')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey('usuarios.PerfilUsuario', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='danados/', blank=True, null=True)
    cantidad_recuperada = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.empresa_id:
            if self.ubicacion_id:
                self.empresa = self.ubicacion.empresa
            elif self.producto_id:
                self.empresa = self.producto.empresa
        super().save(*args, **kwargs)
    cantidad_repuesta = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Producto Dañado'
        verbose_name_plural = 'Productos Dañados'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"

    @property
    def cantidad_pendiente(self):
        pendiente = self.cantidad - self.cantidad_recuperada - self.cantidad_repuesta
        return max(0, pendiente)
