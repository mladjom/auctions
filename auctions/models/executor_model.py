from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from django.utils.text import slugify
from django.urls import reverse

class Executor(BaseModel):
    name = models.CharField(_("Name"), max_length=200)
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True)
    jurisdiction = models.CharField(_("Jurisdiction"), max_length=200, blank=True)

    source_field = 'name'  # Use the `name` field for slug generation

    class Meta:
        verbose_name = _("Executor")
        verbose_name_plural = _("Executors")
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Define the absolute URL for an Executor instance.
        """
        return reverse('executor-detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        # Automatically generate slug if not already set
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)