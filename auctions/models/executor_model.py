from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel

class Executor(BaseModel):
    name = models.CharField(_("Name"), max_length=200)
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True)
    jurisdiction = models.CharField(_("Jurisdiction"), max_length=200, blank=True)
    
    class Meta:
        verbose_name = _("Executor")
        verbose_name_plural = _("Executors")
        ordering = ['name']

    def __str__(self):
        return self.name