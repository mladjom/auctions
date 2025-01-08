from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel

class AuctionDocument(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    file = models.FileField(_("File"), upload_to='auction_documents/')
    description = models.TextField(_("Description"), blank=True)
    
    source_field = 'title'  # Use the `name` field for slug generation

    slug = None  # Remove the slug field
    meta_description = None  # Remove the meta_description field    
    
    class Meta:
        verbose_name = _("Auction Document")
        verbose_name_plural = _("Auction Documents")
        ordering = ['-created_at']

    def __str__(self):
        return self.title