# auctions/models/base_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from ..utils.content_utils import normalize_text
from django.utils import timezone

class BaseModel(models.Model):
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug'))
    meta_title = models.CharField(_("Meta Title"), max_length=200, blank=True)
    meta_description = models.TextField(max_length=160, blank=True, verbose_name=_('Meta Description'))
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
    def seo_meta_description(self):
        """
        Use `meta_description` if defined; otherwise, generate a default description.
        Subclasses can override this property if needed.
        """
        return self.meta_description or _("Explore more about %(slug)s.") % {"slug": self.get_slug_source()}

    @property
    def canonical_url(self):
        """
        Generate a canonical URL based on the model's class name and slug.
        """
        return f"/{self.__class__.__name__.lower()}s/{self.slug}/"            
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_slug_source())
        super().save(*args, **kwargs)