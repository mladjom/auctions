from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from django.urls import reverse

class Tag(BaseModel):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['title_sr']

    def __str__(self):
        return self.title_sr

    def get_absolute_url(self):
        return reverse('auctions:tag-detail', kwargs={'slug': self.slug})
