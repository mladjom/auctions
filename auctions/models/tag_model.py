from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from django.urls import reverse

class Tag(BaseModel):
    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True)

    source_field = 'name'  # Define the field to use for slug generation
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Define the absolute URL for a Tag instance.
        """
        return reverse('auctions:tag-detail', kwargs={'slug': self.slug})
