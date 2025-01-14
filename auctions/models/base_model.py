# auctions/models/base_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from auctions.utils.content_utils import normalize_text, transliterate_text
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

    def generate_unique_slug(self, source_text):
        """
        Generate a unique slug from the source text
        """
        base_slug = slugify(normalize_text(source_text))
        if not base_slug:
            base_slug = f"unnamed-{self.__class__.__name__.lower()}"
        
        # Query existing objects of this class
        model_class = self.__class__
        existing_objects = model_class.objects.filter(slug__startswith=base_slug)
        
        if not existing_objects.exists():
            return base_slug
            
        # Find the highest number suffix
        max_suffix = 0
        for obj in existing_objects:
            try:
                # Split the slug and get the number suffix if it exists
                suffix = obj.slug.replace(f"{base_slug}-", "")
                if suffix.isdigit():
                    max_suffix = max(max_suffix, int(suffix))
            except (ValueError, AttributeError):
                continue
        
        # Return new slug with incremented suffix
        return f"{base_slug}-{max_suffix + 1}"

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
            self.title_lat = transliterate_text(self.title_sr)
        if not self.description_lat and self.description_sr:
            self.description_lat = transliterate_text(self.description_sr)
        if not self.meta_title_lat and self.meta_title_sr:
            self.meta_title_lat = transliterate_text(self.meta_title_sr)
        if not self.meta_description_lat and self.meta_description_sr:
            self.meta_description_lat = transliterate_text(self.meta_description_sr)

        # Generate slug from Latin title
        if not self.slug and self.title_sr:
            self.slug = slugify(self.title_lat or transliterate_text(self.title_sr))
            
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