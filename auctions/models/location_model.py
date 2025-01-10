from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from django.urls import reverse
from django.utils.text import slugify

class Location(BaseModel):
    municipality = models.CharField(_("Municipality"), max_length=100, blank=True)
    city = models.CharField(_("City"), max_length=100)
    cadastral_municipality = models.CharField(_("Cadastral Municipality"), max_length=100, blank=True)

    source_field = 'city'  # Use the `city` field for slug generation

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        ordering = ['city', 'municipality']

    def __str__(self):
        return f"{self.city}, {self.municipality}" if self.municipality else self.city

    def get_absolute_url(self):
        """
        Define the absolute URL for a Location instance.
        """
        return reverse('location-detail', kwargs={'slug': self.slug})
