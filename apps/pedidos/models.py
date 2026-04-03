from django.db import models
from django.contrib.auth.models import User
from apps.productos.models import Producto
from apps.usuarios.models import PerfilUsuario

from apps.core.tenancy import EmpresaOwnedModel
import uuid
from datetime import datetime

class Pedido(EmpresaOwnedModel):
    """Registro de pedidos entre ubicaciones"""
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('enviado', 'Enviado'),
        ('recibido', 'Recibido'),
        ('cancelado', 'Cancelado'),
    )
    
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='pedidos')
    codigo = models.CharField(max_length=50, unique=True)
    solicitante = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='pedidos_realizados')
    proveedor = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='pedidos_recibidos')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    comentario = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.codigo} - {self.solicitante} → {self.proveedor}"

    def save(self, *args, **kwargs):
        if not self.empresa_id and self.solicitante_id:
            self.empresa = self.solicitante.empresa
        super().save(*args, **kwargs)

    @classmethod
    def generar_codigo(cls):
        prefijo = 'PED'
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        aleatorio = str(uuid.uuid4())[:8].upper()
        return f"{prefijo}-{timestamp}-{aleatorio}"

    @property
    def total_productos(self):
        return self.detalles.count()


class DetallePedido(EmpresaOwnedModel):
    """Detalle de productos en el pedido"""
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, null=True, blank=True, related_name='detalles_pedidos')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"

    def save(self, *args, **kwargs):
        if not self.empresa_id and self.pedido_id:
            self.empresa = self.pedido.empresa
        super().save(*args, **kwargs)
