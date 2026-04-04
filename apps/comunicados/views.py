from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Comunicado, ComunicadoLectura


@user_passes_test(lambda u: u.is_superuser)
def comunicados_list(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "crear_comunicado":
            titulo = (request.POST.get("titulo") or "").strip()
            mensaje = (request.POST.get("mensaje") or "").strip()
            publicar = request.POST.get("publicar") == "on"

            if not titulo or not mensaje:
                messages.error(request, "Título y mensaje son obligatorios.")
                return redirect("comunicados_list")

            comunicado = Comunicado.objects.create(
                titulo=titulo,
                mensaje=mensaje,
                creado_por=request.user,
            )

            if publicar:
                comunicado.publicado = True
                comunicado.fecha_publicacion = timezone.now()
                comunicado.save(update_fields=["publicado", "fecha_publicacion", "fecha_actualizacion"])

            messages.success(request, "Comunicado creado.")
            return redirect("comunicados_list")

        if action == "editar_comunicado":
            comunicado_id = request.POST.get("comunicado_id")
            comunicado = get_object_or_404(Comunicado, id=comunicado_id)

            titulo = (request.POST.get("titulo") or "").strip()
            mensaje = (request.POST.get("mensaje") or "").strip()

            if not titulo or not mensaje:
                messages.error(request, "Título y mensaje son obligatorios.")
                return redirect("comunicados_list")

            comunicado.titulo = titulo
            comunicado.mensaje = mensaje
            comunicado.save(update_fields=["titulo", "mensaje", "fecha_actualizacion"])

            messages.success(request, "Comunicado actualizado.")
            return redirect("comunicados_list")

        if action == "toggle_publicado":
            comunicado_id = request.POST.get("comunicado_id")
            comunicado = get_object_or_404(Comunicado, id=comunicado_id)

            if not comunicado.publicado:
                comunicado.publicado = True
                comunicado.fecha_publicacion = timezone.now()
                comunicado.save(update_fields=["publicado", "fecha_publicacion", "fecha_actualizacion"])
                messages.success(request, "Comunicado publicado.")
            else:
                comunicado.publicado = False
                comunicado.save(update_fields=["publicado", "fecha_actualizacion"])
                messages.success(request, "Comunicado despublicado.")

            return redirect("comunicados_list")

        if action == "toggle_activo":
            comunicado_id = request.POST.get("comunicado_id")
            comunicado = get_object_or_404(Comunicado, id=comunicado_id)

            comunicado.activo = not comunicado.activo
            comunicado.save(update_fields=["activo", "fecha_actualizacion"])

            messages.success(request, "Comunicado activado." if comunicado.activo else "Comunicado desactivado.")
            return redirect("comunicados_list")

    comunicados = Comunicado.objects.all().order_by("-fecha_creacion")

    context = {
        "comunicados": comunicados,
    }
    return render(request, "comunicados/comunicados.html", context)


@login_required
def historial_comunicados(request):
    comunicados = list(
        Comunicado.objects.filter(publicado=True, activo=True).order_by(
            "-fecha_publicacion", "-fecha_creacion"
        )
    )

    leidos = set(
        ComunicadoLectura.objects.filter(
            usuario=request.user,
            comunicado_id__in=[c.id for c in comunicados],
        ).values_list("comunicado_id", flat=True)
    )

    items = []
    for c in comunicados:
        items.append(
            {
                "obj": c,
                "leido": c.id in leidos,
            }
        )

    context = {
        "items": items,
    }
    return render(request, "comunicados/historial.html", context)


@login_required
def detalle_comunicado(request, id: int):
    comunicado = get_object_or_404(Comunicado, id=id, publicado=True, activo=True)
    ComunicadoLectura.objects.get_or_create(comunicado=comunicado, usuario=request.user)

    context = {
        "comunicado": comunicado,
    }
    return render(request, "comunicados/detalle.html", context)


@login_required
def obtener_comunicados(request):
    """Obtener comunicados publicados en JSON para el dropdown del navbar."""
    try:
        comunicados = list(
            Comunicado.objects.filter(publicado=True, activo=True).order_by(
                "-fecha_publicacion", "-fecha_creacion"
            )[:10]
        )

        leidos = set(
            ComunicadoLectura.objects.filter(
                usuario=request.user,
                comunicado_id__in=[c.id for c in comunicados],
            ).values_list("comunicado_id", flat=True)
        )

        data = []
        for com in comunicados:
            ts = com.fecha_publicacion or com.fecha_creacion
            minutos_atras = (timezone.now() - ts).total_seconds() / 60

            if minutos_atras < 1:
                tiempo_text = "Ahora"
            elif minutos_atras < 60:
                tiempo_text = f"Hace {int(minutos_atras)} min"
            elif minutos_atras < 1440:
                horas = int(minutos_atras / 60)
                tiempo_text = f"Hace {horas} hora{'s' if horas > 1 else ''}"
            else:
                dias = int(minutos_atras / 1440)
                tiempo_text = f"Hace {dias} día{'s' if dias > 1 else ''}"

            data.append(
                {
                    "id": com.id,
                    "titulo": com.titulo,
                    "mensaje": com.mensaje,
                    "icono": "fa-bullhorn bg-info",
                    "tiempo": tiempo_text,
                    "leida": com.id in leidos,
                    "url": f"/comunicados/{com.id}/",
                }
            )

        total = Comunicado.objects.filter(publicado=True, activo=True).count()
        leidos_total = ComunicadoLectura.objects.filter(
            usuario=request.user,
            comunicado__publicado=True,
            comunicado__activo=True,
        ).count()
        no_leidas = max(0, total - leidos_total)

        return JsonResponse({"comunicados": data, "no_leidas": no_leidas})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def contador_comunicados(request):
    try:
        total = Comunicado.objects.filter(publicado=True, activo=True).count()
        leidos_total = ComunicadoLectura.objects.filter(
            usuario=request.user,
            comunicado__publicado=True,
            comunicado__activo=True,
        ).count()
        no_leidas = max(0, total - leidos_total)
        return JsonResponse({"no_leidas": no_leidas})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def marcar_comunicado_leido(request, id: int):
    try:
        comunicado = Comunicado.objects.filter(id=id, publicado=True, activo=True).first()
        if not comunicado:
            return JsonResponse({"error": "Comunicado no encontrado"}, status=404)

        ComunicadoLectura.objects.get_or_create(comunicado=comunicado, usuario=request.user)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def marcar_todos_comunicados_leidos(request):
    try:
        comunicados_ids = list(
            Comunicado.objects.filter(publicado=True, activo=True).values_list("id", flat=True)
        )

        existentes = set(
            ComunicadoLectura.objects.filter(
                usuario=request.user,
                comunicado_id__in=comunicados_ids,
            ).values_list("comunicado_id", flat=True)
        )

        nuevos = [
            ComunicadoLectura(comunicado_id=com_id, usuario=request.user)
            for com_id in comunicados_ids
            if com_id not in existentes
        ]
        if nuevos:
            ComunicadoLectura.objects.bulk_create(nuevos)

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
