from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from django.urls import reverse
from django.db import models

class Category(BaseModel):
    """Category model for organizing content"""
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='children'
    )
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        
    def get_schema_data(self):
        """Override schema data for categories"""
        base_schema = super().get_schema_data()
        base_schema.update({
            "@type": "CategoryCode",
            "codeValue": self.slug,
        })
        return base_schema
