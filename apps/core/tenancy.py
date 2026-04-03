from threading import local

from django.db import models


_thread_locals = local()


def set_current_empresa(empresa):
    _thread_locals.empresa = empresa


def get_current_empresa():
    return getattr(_thread_locals, "empresa", None)


class EmpresaQuerySet(models.QuerySet):
    def for_empresa(self, empresa):
        if empresa is None:
            return self
        return self.filter(empresa=empresa)


class EmpresaManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        empresa = get_current_empresa()
        if empresa is None:
            return qs
        return qs.filter(empresa=empresa)

    def for_empresa(self, empresa):
        return self.get_queryset().filter(empresa=empresa)


class EmpresaOwnedModel(models.Model):
    objects = EmpresaManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if hasattr(self, "empresa") and not getattr(self, "empresa_id", None):
            empresa = get_current_empresa()
            if empresa is not None:
                self.empresa = empresa
        super().save(*args, **kwargs)
