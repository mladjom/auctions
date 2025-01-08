from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel

class Location(BaseModel):
    municipality = models.CharField(_("Municipality"), max_length=100, blank=True)
    city = models.CharField(_("City"), max_length=100)
    cadastral_municipality = models.CharField(_("Cadastral Municipality"), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        ordering = ['city', 'municipality']

    def __str__(self):
        return f"{self.city}, {self.municipality}"