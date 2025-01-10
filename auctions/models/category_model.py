from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from django.urls import reverse
from django.utils.text import slugify

class Category(BaseModel):
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    
    source_field = 'name'  # Define the field to use for slug generation

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Define the absolute URL for a Category instance.
        """
        return reverse('category-detail', kwargs={'slug': self.slug})
