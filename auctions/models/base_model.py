# auctions/models/base_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from auctions.utils.content_utils import SerbianTextConverter
from django.utils import timezone
from django.utils.translation import get_language

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

    class Meta:
        abstract = True
        
    def get_absolute_url(self):
        """
        Override this method in subclasses for proper URL resolution.
        """
        raise NotImplementedError("Subclasses must implement `get_absolute_url`")

    def get_slug_source(self):
        if hasattr(self, 'source_field'):
            source_value = getattr(self, self.source_field)
            if source_value:
                return source_value
        return f"{self.__class__.__name__.lower()}-{timezone.now().timestamp()}"

    @property
    def canonical_url(self):
        """
        Generate a canonical URL based on the model's class name and slug.
        """
        return f"/{self.__class__.__name__.lower()}s/{self.slug}/"            
    
        
    def save(self, *args, **kwargs):
        # Auto-generate Latin versions if not provided
        if not self.title_lat and self.title_sr:
            self.title_lat = SerbianTextConverter.to_latin(self.title_sr)
        if not self.description_lat and self.description_sr:
            self.description_lat = SerbianTextConverter.to_latin(self.description_sr)
        if not self.meta_title_lat and self.meta_title_sr:
            self.meta_title_lat = SerbianTextConverter.to_latin(self.meta_title_sr)
        if not self.meta_description_lat and self.meta_description_sr:
            self.meta_description_lat = SerbianTextConverter.to_latin(self.meta_description_sr)

        # Generate or update the slug
        if not self.slug:
            self.slug = SerbianTextConverter.generate_unique_slug(
                source_text=self.title_lat or SerbianTextConverter.to_latin(self.title_sr),
                model_class=self.__class__,
                existing_instance=self,
            )

        super().save(*args, **kwargs)

    @property
    def title(self):
        return self.title_lat if get_language() == 'sr-Latn' else self.title_sr

    @property
    def description(self):
        return self.description_lat if get_language() == 'sr-Latn' else self.description_sr

    @property
    def meta_title(self):
        current_title = self.meta_title_lat if get_language() == 'sr-Latn' else self.meta_title_sr
        return current_title or self.title

    @property
    def meta_description(self):
        current_desc = self.meta_description_lat if get_language() == 'sr-Latn' else self.meta_description_sr
        return current_desc or self.description[:160]