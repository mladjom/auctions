from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from django.utils.text import slugify
from django.urls import reverse

class Executor(BaseModel):
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True)
    jurisdiction = models.CharField(_("Jurisdiction"), max_length=200, blank=True)


    class Meta:
        verbose_name = _("Executor")
        verbose_name_plural = _("Executors")
        ordering = ['title_sr']

    def __str__(self):
        return self.title_sr


    def get_absolute_url(self):
        """
        Define the absolute URL for an Executor instance.
        """
        return reverse('auctions:executor-detail', kwargs={'slug': self.slug})
