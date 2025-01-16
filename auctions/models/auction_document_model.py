from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel

class AuctionDocument(BaseModel):
    file = models.FileField(_("File"), upload_to='auction_documents/')
    

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
        verbose_name = _("Auction Document")
        verbose_name_plural = _("Auction Documents")
        ordering = ['-created_at']

    def __str__(self):
        return self.title