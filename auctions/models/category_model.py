from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from django.urls import reverse

class Category(BaseModel):
    
    source_field = 'title_lat'  # Add this line to specify slug source
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['title_sr']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('auctions:category-detail', kwargs={'slug': self.slug})
