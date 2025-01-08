from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel

class Tag(BaseModel):
    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True)
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name']

    def __str__(self):
        return self.name