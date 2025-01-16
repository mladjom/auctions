from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel

class Image(BaseModel):
    file = models.ImageField(_("File"), upload_to='auction_images/')
    alt_text = models.CharField(_("Alt text"), max_length=200, blank=True)
    caption = models.TextField(_("Caption"), blank=True)


    slug = None  # Remove the slug field
    description_sr = None  # Remove the meta_description field    
    description_lat = None  # Remove the meta_description field    
    meta_title_sr = None  # Remove the meta_description field    
    meta_title_lat = None  # Remove the meta_description field    
    meta_description_sr = None  # Remove the meta_description field    
    meta_description_lat = None  # Remove the meta_description field    
    is_active = None 
    view_count = None
      
    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        ordering = ['-created_at']

    def __str__(self):
        return self.title