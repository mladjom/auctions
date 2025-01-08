from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel

class Image(BaseModel):
    title = models.CharField(_("Title"), max_length=200)
    file = models.ImageField(_("File"), upload_to='auction_images/')
    alt_text = models.CharField(_("Alt text"), max_length=200, blank=True)
    caption = models.TextField(_("Caption"), blank=True)

    source_field = 'title'  # Use the `name` field for slug generation

    slug = None  # Remove the slug field
    meta_description = None  # Remove the meta_description field   
        
    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        ordering = ['-created_at']

    def __str__(self):
        return self.title