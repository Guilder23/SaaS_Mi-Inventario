from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.empresas.models import Empresa, PagoEmpresa
from apps.planes.models import Plan
from apps.productos.models import Producto
from apps.usuarios.models import PerfilUsuario


@login_required(login_url='index')
def dashboard(request):
    """Vista principal del dashboard - Muestra métricas clave del sistema"""

    from django.db.models import F

    from apps.inventario.models import Inventario, MovimientoInventario
    from apps.pedidos.models import Pedido
    from apps.traspasos.models import Traspaso
    from apps.ventas.models import DetalleVenta, Venta
    
    # ======= PRODUCTOS Y STOCK =======
    # Total de productos activos registrados
    total_productos = Producto.objects.filter(activo=True).count()
    
    # Productos con stock disponible en todas las ubicaciones
    productos_en_stock = Inventario.objects.filter(cantidad__gt=0).values('producto').distinct().count()
    
    # Stock crítico: productos bajo mínimo requerido
    inventario_critico = Inventario.objects.select_related('producto', 'ubicacion').filter(
        cantidad__lte=F('producto__stock_critico')
    ).count()
    
    # Stock bajo: productos cerca del mínimo
    inventario_bajo = Inventario.objects.select_related('producto', 'ubicacion').filter(
        cantidad__lte=F('producto__stock_bajo'),
        cantidad__gt=F('producto__stock_critico')
    ).count()
    
    # ======= VENTAS =======
    # Fecha de inicio del mes actual
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total vendido en el mes actual (todas las monedas)
    ventas_mes = Venta.objects.filter(
        fecha_elaboracion__gte=inicio_mes,
        estado='completada'
    )
    total_ventas_mes_bob = ventas_mes.filter(moneda='BOB').aggregate(total=Sum('total'))['total'] or Decimal('0')
    total_ventas_mes_usd = ventas_mes.filter(moneda='USD').aggregate(total=Sum('total'))['total'] or Decimal('0')
    cantidad_ventas_mes = ventas_mes.count()
    
    # Ventas del día
    hoy = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ventas_hoy = Venta.objects.filter(fecha_elaboracion__gte=hoy, estado='completada').count()
    
    # Ventas pendientes
    ventas_pendientes = Venta.objects.filter(estado='pendiente').count()
    
    # ======= TRASPASOS Y PEDIDOS =======
    # Traspasos pendientes de atención
    traspasos_pendientes = Traspaso.objects.filter(estado='PENDIENTE').count()
    
    # Pedidos pendientes de completar
    pedidos_pendientes = Pedido.objects.filter(estado='PENDIENTE').count()
    
    # ======= MOVIMIENTOS RECIENTES =======
    # Últimos 10 movimientos de inventario
    ultimos_movimientos = MovimientoInventario.objects.select_related(
        'producto', 'ubicacion'
    ).order_by('-fecha')[:10]
    
    # ======= ÚLTIMAS VENTAS =======
    # Últimas 10 ventas registradas
    ultimas_ventas = Venta.objects.select_related(
        'ubicacion', 'vendedor'
    ).order_by('-fecha_elaboracion')[:10]
    
    # ======= PRODUCTOS MÁS VENDIDOS DEL MES =======
    # Top 5 productos más vendidos este mes
    productos_mas_vendidos = DetalleVenta.objects.filter(
        venta__fecha_elaboracion__gte=inicio_mes,
        venta__estado='completada'
    ).values(
        'producto__id',
        'producto__codigo',
        'producto__nombre'
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    # ======= STOCK CRÍTICO DETALLADO =======
    # Productos en estado crítico para alertas
    productos_stock_critico = Inventario.objects.select_related(
        'producto', 'ubicacion'
    ).filter(
        cantidad__lte=F('producto__stock_critico')
    ).order_by('cantidad')[:10]
    
    context = {
        # Productos y stock
        'total_productos': total_productos,
        'productos_en_stock': productos_en_stock,
        'inventario_critico': inventario_critico,
        'inventario_bajo': inventario_bajo,
        
        # Ventas
        'total_ventas_mes_bob': total_ventas_mes_bob,
        'total_ventas_mes_usd': total_ventas_mes_usd,
        'cantidad_ventas_mes': cantidad_ventas_mes,
        'ventas_hoy': ventas_hoy,
        'ventas_pendientes': ventas_pendientes,
        
        # Traspasos y pedidos
        'traspasos_pendientes': traspasos_pendientes,
        'pedidos_pendientes': pedidos_pendientes,
        
        # Actividad reciente
        'ultimos_movimientos': ultimos_movimientos,
        'ultimas_ventas': ultimas_ventas,
        'productos_mas_vendidos': productos_mas_vendidos,
        'productos_stock_critico': productos_stock_critico,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


def _month_start(dt):
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _months_back_labels(*, months: int) -> list[tuple[int, int, str]]:
    """Retorna [(year, month, label)] desde hace N-1 meses hasta el actual."""
    now = timezone.now()
    start = _month_start(now) - timedelta(days=31 * (months - 1))
    # Normalizar a primer día de mes
    start = start.replace(day=1)

    out: list[tuple[int, int, str]] = []
    cur = start
    for _ in range(months):
        out.append((cur.year, cur.month, cur.strftime('%b %Y')))
        # Avanzar 1 mes sin depender de librerías externas
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)
    return out


@login_required(login_url='index')
def superadmin_dashboard(request):
    """Dashboard SaaS para superusuario (visión global multi-empresa)."""
    if not request.user.is_superuser:
        return redirect('dashboard')

    # =====================
    # KPIs
    # =====================
    total_empresas = Empresa.objects.count()
    total_usuarios = (
        PerfilUsuario.all_objects.filter(
            activo=True,
            usuario__isnull=False,
            usuario__is_active=True,
        )
        .exclude(usuario__username__startswith='deposito_auto_')
        .count()
    )
    total_productos = Producto.all_objects.filter(activo=True).count()

    inicio_mes = _month_start(timezone.now())
    pagos_mes = PagoEmpresa.objects.filter(estado='aprobado', fecha_envio__gte=inicio_mes)
    ingresos_mes_bob = pagos_mes.filter(moneda='BOB').aggregate(total=Sum('monto'))['total'] or Decimal('0')
    ingresos_mes_usd = pagos_mes.filter(moneda='USD').aggregate(total=Sum('monto'))['total'] or Decimal('0')

    nuevas_empresas_mes = Empresa.objects.filter(fecha_creacion__gte=inicio_mes).count()

    # =====================
    # Agregados por empresa
    # =====================
    users_by_empresa = {
        row['empresa']: row['c']
        for row in PerfilUsuario.all_objects.filter(
            activo=True,
            usuario__isnull=False,
            usuario__is_active=True,
        )
        .exclude(usuario__username__startswith='deposito_auto_')
        .values('empresa')
        .annotate(c=Count('id'))
    }

    products_by_empresa = {
        row['empresa']: row['c']
        for row in Producto.all_objects.filter(activo=True)
        .values('empresa')
        .annotate(c=Count('id'))
    }

    # =====================
    # Alertas
    # =====================
    planes = {p.codigo: p for p in Plan.objects.filter(activo=True)}
    alertas_cerca_limite = []
    for empresa in Empresa.objects.all().order_by('nombre'):
        plan_obj = planes.get(empresa.plan)
        usados_u = users_by_empresa.get(empresa.id, 0)
        usados_p = products_by_empresa.get(empresa.id, 0)

        if plan_obj and plan_obj.max_usuarios_total:
            limite_u = plan_obj.max_usuarios_total
            if limite_u > 0 and usados_u / limite_u >= 0.8:
                alertas_cerca_limite.append({
                    'empresa': empresa,
                    'tipo': 'Usuarios',
                    'usados': usados_u,
                    'limite': limite_u,
                    'porcentaje': int((usados_u / limite_u) * 100),
                })

        if plan_obj and plan_obj.max_productos:
            limite_p = plan_obj.max_productos
            if limite_p > 0 and usados_p / limite_p >= 0.8:
                alertas_cerca_limite.append({
                    'empresa': empresa,
                    'tipo': 'Productos',
                    'usados': usados_p,
                    'limite': limite_p,
                    'porcentaje': int((usados_p / limite_p) * 100),
                })

    alertas_cerca_limite = sorted(alertas_cerca_limite, key=lambda x: x['porcentaje'], reverse=True)[:10]

    hoy = timezone.now().date()
    empresas_suspendidas = list(
        Empresa.objects.filter(activa=False).order_by('-fecha_actualizacion')[:10]
    )
    empresas_vencidas = list(
        Empresa.objects.filter(activa=True, fecha_vencimiento__isnull=False, fecha_vencimiento__lt=hoy)
        .order_by('fecha_vencimiento')[:10]
    )

    # Empresas "sin pago": sin pago aprobado o con pago pendiente
    empresas_con_pago_aprobado_ids = set(
        PagoEmpresa.objects.filter(estado='aprobado').values_list('empresa_id', flat=True).distinct()
    )
    empresas_con_pago_pendiente_ids = set(
        PagoEmpresa.objects.filter(estado='pendiente').values_list('empresa_id', flat=True).distinct()
    )
    empresas_sin_pago = list(
        Empresa.objects.exclude(id__in=empresas_con_pago_aprobado_ids).order_by('-fecha_creacion')[:10]
    )

    # =====================
    # Actividad reciente (feed)
    # =====================
    eventos = []
    for e in Empresa.objects.all().order_by('-fecha_creacion')[:10]:
        eventos.append({
            'ts': e.fecha_creacion,
            'icono': 'fa-building',
            'texto': f"Nueva empresa registrada: {e.nombre}",
        })
    for u in PerfilUsuario.all_objects.select_related('empresa', 'usuario').filter(
        usuario__isnull=False,
    ).exclude(usuario__username__startswith='deposito_auto_').order_by('-fecha_creacion')[:10]:
        if u.empresa and u.usuario:
            eventos.append({
                'ts': u.fecha_creacion,
                'icono': 'fa-user-plus',
                'texto': f"{u.empresa.nombre}: nuevo usuario {u.usuario.username} ({u.get_rol_display()})",
            })
    for p in Producto.all_objects.select_related('empresa').filter(activo=True).order_by('-fecha_creacion')[:10]:
        if p.empresa:
            eventos.append({
                'ts': p.fecha_creacion,
                'icono': 'fa-box',
                'texto': f"{p.empresa.nombre}: nuevo producto {p.nombre}",
            })
    for pago in PagoEmpresa.objects.select_related('empresa').filter(estado='aprobado').order_by('-fecha_envio')[:10]:
        eventos.append({
            'ts': pago.fecha_envio,
            'icono': 'fa-credit-card',
            'texto': f"Pago aprobado: {pago.empresa.nombre} ({pago.monto} {pago.moneda})",
        })

    eventos = sorted(eventos, key=lambda x: x['ts'], reverse=True)[:8]

    # =====================
    # Gráficas (series 12 meses)
    # =====================
    months = _months_back_labels(months=12)
    start_dt = _month_start(timezone.now()) - timedelta(days=31 * 11)
    start_dt = start_dt.replace(day=1)

    empresas_mes_qs = (
        Empresa.objects.filter(fecha_creacion__gte=start_dt)
        .annotate(m=TruncMonth('fecha_creacion'))
        .values('m')
        .annotate(c=Count('id'))
        .order_by('m')
    )
    empresas_mes_map = {(row['m'].year, row['m'].month): row['c'] for row in empresas_mes_qs if row['m']}

    ingresos_mes_qs = (
        PagoEmpresa.objects.filter(estado='aprobado', moneda='BOB', fecha_envio__gte=start_dt)
        .annotate(m=TruncMonth('fecha_envio'))
        .values('m')
        .annotate(total=Sum('monto'))
        .order_by('m')
    )
    ingresos_mes_map = {(row['m'].year, row['m'].month): float(row['total'] or 0) for row in ingresos_mes_qs if row['m']}

    labels = [lbl for (_y, _m, lbl) in months]
    empresas_series = [empresas_mes_map.get((y, m), 0) for (y, m, _lbl) in months]
    ingresos_series = [ingresos_mes_map.get((y, m), 0) for (y, m, _lbl) in months]

    # Distribución de planes
    planes_dist_raw = Empresa.objects.values('plan').annotate(c=Count('id')).order_by('-c')
    planes_labels = []
    planes_values = []
    for row in planes_dist_raw:
        codigo = row['plan']
        plan_obj = planes.get(codigo)
        planes_labels.append(plan_obj.nombre if plan_obj else codigo)
        planes_values.append(row['c'])

    # Top 5 usuarios por empresa
    top_users = (
        PerfilUsuario.all_objects.filter(
            activo=True,
            usuario__isnull=False,
            usuario__is_active=True,
            empresa__isnull=False,
        )
        .exclude(usuario__username__startswith='deposito_auto_')
        .values('empresa__nombre')
        .annotate(c=Count('id'))
        .order_by('-c')[:5]
    )
    top_users_labels = [r['empresa__nombre'] for r in top_users]
    top_users_values = [r['c'] for r in top_users]

    # Productos por empresa (top 10)
    top_products = (
        Producto.all_objects.filter(activo=True, empresa__isnull=False)
        .values('empresa__nombre')
        .annotate(c=Count('id'))
        .order_by('-c')[:10]
    )
    top_products_labels = [r['empresa__nombre'] for r in top_products]
    top_products_values = [r['c'] for r in top_products]

    charts_data = {
        'labels': labels,
        'empresas': empresas_series,
        'ingresos': ingresos_series,
        'planes': {
            'labels': planes_labels,
            'values': planes_values,
        },
        'topUsuarios': {
            'labels': top_users_labels,
            'values': top_users_values,
        },
        'topProductos': {
            'labels': top_products_labels,
            'values': top_products_values,
        },
    }

    context = {
        'total_empresas': total_empresas,
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'ingresos_mes_bob': ingresos_mes_bob,
        'ingresos_mes_usd': ingresos_mes_usd,
        'nuevas_empresas_mes': nuevas_empresas_mes,

        'alertas_cerca_limite': alertas_cerca_limite,
        'empresas_suspendidas': empresas_suspendidas,
        'empresas_vencidas': empresas_vencidas,
        'empresas_sin_pago': empresas_sin_pago,
        'empresas_con_pago_pendiente_ids_json': json.dumps(list(empresas_con_pago_pendiente_ids)),

        'eventos': eventos,
        'charts_data': charts_data,
    }

    return render(request, 'dashboard/superadmin_dashboard.html', context)


def index(request):
    """Página principal con modal de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    context = {
        'roles': getattr(PerfilUsuario, 'ROLES', [])
    }
    return render(request, 'index.html', context)
