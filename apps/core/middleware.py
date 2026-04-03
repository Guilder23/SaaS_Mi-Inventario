from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

from apps.core.tenancy import set_current_empresa


class EmpresaActivaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        empresa = None
        rutas_libres = [
            "/inicio/",
            "/login/",
            "/empresas/pagos/",
        ]
        try:
            if request.user.is_authenticated and not request.user.is_superuser:
                perfil = getattr(request.user, "perfil", None)
                empresa = getattr(perfil, "empresa", None) if perfil else None

                if not empresa:
                    logout(request)
                    messages.error(request, "Usuario sin empresa asignada.")
                    return redirect("index")

                if not empresa.esta_activa and not any(request.path.startswith(ruta) for ruta in rutas_libres):
                    logout(request)
                    messages.error(request, "Empresa inactiva o con pago vencido.")
                    return redirect("index")

            set_current_empresa(empresa)
            request.empresa = empresa
            response = self.get_response(request)
            return response
        finally:
            set_current_empresa(None)
