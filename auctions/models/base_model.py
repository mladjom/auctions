from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.db.models import F
from auctions.utils.content_utils import SerbianTextConverter
from django.urls import reverse

class BaseModel(models.Model):
    # Core fields in both scripts
    title_sr = models.CharField(_("Title (Cyrillic)"), max_length=255)
    title_lat = models.CharField(_("Title (Latin)"), max_length=255, blank=True)
    description_sr = models.TextField(_("Description (Cyrillic)"), blank=True)
    description_lat = models.TextField(_("Description (Latin)"), blank=True)
    
    # SEO fields in both scripts
    meta_title_sr = models.CharField(_("Meta Title (Cyrillic)"), max_length=200, blank=True)
    meta_title_lat = models.CharField(_("Meta Title (Latin)"), max_length=200, blank=True)
    meta_description_sr = models.TextField(_("Meta Description (Cyrillic)"), max_length=160, blank=True)
    meta_description_lat = models.TextField(_("Meta Description (Latin)"), max_length=160, blank=True)
    
    # Common fields
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug'))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Get the absolute URL for the object"""
        return reverse(f"{self._meta.app_label}:{self._meta.model_name}-detail", 
                      kwargs={'slug': self.slug})
    
    def increment_view_count(self):
        """Increment the view count atomically"""
        self.__class__.objects.filter(pk=self.pk).update(view_count=F('view_count') + 1)

    @property
    def title(self):
        return self.title_sr if get_language() == 'sr' else self.title_lat

    @property
    def description(self):
        return self.description_sr if get_language() == 'sr' else self.description_lat

    @property
    def meta_title(self):
        current_title = self.meta_title_sr if get_language() == 'sr' else self.meta_title_lat
        return current_title or self.title

    @property
    def meta_description(self):
        current_desc = self.meta_description_sr if get_language() == 'sr' else self.meta_description_lat
        return current_desc or self.description[:160]

    @property
    def canonical_url(self):
        return self.get_absolute_url()

    def save(self, *args, **kwargs):
        # Auto-generate Latin versions if not provided
        if not self.title_lat and self.title_sr:
            self.title_lat = SerbianTextConverter.to_latin(self.title_sr)
        if hasattr(self, 'description_sr') and hasattr(self, 'description_lat') and not self.description_lat and self.description_sr:
            self.description_lat = SerbianTextConverter.to_latin(self.description_sr)
        if hasattr(self, 'meta_title_sr') and hasattr(self, 'meta_title_lat') and not self.meta_title_lat and self.meta_title_sr:
            self.meta_title_lat = SerbianTextConverter.to_latin(self.meta_title_sr)
        if hasattr(self, 'meta_description_sr') and hasattr(self, 'meta_description_lat') and not self.meta_description_lat and self.meta_description_sr:
            self.meta_description_lat = SerbianTextConverter.to_latin(self.meta_description_sr)

        # Generate or update the slug only if the model has a slug field
        if hasattr(self, 'slug') and self.__class__.slug is not None:
            if not self.slug:
                self.slug = SerbianTextConverter.generate_unique_slug(
                    source_text=self.title_lat or SerbianTextConverter.to_latin(self.title_sr),
                    model_class=self.__class__,
                    existing_instance=self,
                )

        super().save(*args, **kwargs)


    def get_schema_data(self):
        """Get schema.org structured data"""
        return {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": self.title,
            "description": self.description,
            "inLanguage": "sr" if get_language() == 'sr' else "sr-Latn",
            "datePublished": self.created_at.isoformat(),
            "dateModified": self.updated_at.isoformat(),
            "url": self.get_absolute_url()
        } 