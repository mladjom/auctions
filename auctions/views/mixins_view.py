# views/mixins_view.py
from django.utils.translation import gettext_lazy as _, get_language
from django.urls import reverse

class LanguageAwareMixin:
    """Mixin for handling language-specific content and URLs"""
    
    def get_language_specific_url(self, url_name, **kwargs):
        """Get language-specific URL with proper prefix"""
        if not url_name:
            return '/'
        
        current_language = get_language()
        url = reverse(url_name, kwargs=kwargs)
        return f'/sr-Latn{url}' if current_language == 'sr-Latn' else url
    
    def get_language_specific_fields(self):
        """Get field names based on current language"""
        suffix = '_sr' if get_language() == 'sr' else '_lat'
        return {
            'title': f'title{suffix}',
            'description': f'description{suffix}',
            'meta_title': f'meta_title{suffix}',
            'meta_description': f'meta_description{suffix}'
        }
    
    def get_breadcrumbs(self):
        """Get base breadcrumbs"""
        return [{
            'title': _('Home'),
            'url': self.get_language_specific_url('home')
        }]

class SchemaMixin:
    """Mixin for handling JSON-LD schema data"""
    
    def get_base_schema(self):
        """Get base schema data common to all pages"""
        return {
            "@context": "https://schema.org",
            "inLanguage": "sr" if get_language() == 'sr' else "sr-Latn",
            "url": self.request.build_absolute_uri()
        }
    
    def get_breadcrumb_schema(self, breadcrumbs):
        """Generate schema for breadcrumbs"""
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": crumb['title'],
                    "item": self.request.build_absolute_uri(crumb['url'])
                } for i, crumb in enumerate(breadcrumbs) if crumb['url']
            ]
        }
    
    def get_list_schema(self, items):
        """Generate schema for list views"""
        return {
            **self.get_base_schema(),
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": {
                        "@type": "Thing",
                        "url": self.request.build_absolute_uri(item.get_absolute_url()),
                        "name": item.title,
                        "description": item.description
                    }
                } for i, item in enumerate(items, start=1)
            ]
        }
    
    def get_detail_schema(self, obj):
        """Generate schema for detail views"""
        return {
            **self.get_base_schema(),
            "@type": "WebPage",
            "mainEntity": obj.get_schema_data(),
            "breadcrumb": self.get_breadcrumb_schema(self.get_breadcrumbs())
        }

class SEOMixin:
    """Mixin for handling meta tags and SEO"""
    
    def get_meta_tags(self):
        """Get meta tags with language-specific content"""
        if hasattr(self, 'object'):
            return {
                'meta_title': self.object.meta_title,
                'meta_description': self.object.meta_description,
                'og_title': self.object.meta_title,
                'og_description': self.object.meta_description,
                'og_type': 'article'
            }
        return {}
    
class URLHandlerMixin:
    """Mixin for handling canonical and alternate URLs"""
    def get_url_variants(self):
        current_url = self.request.build_absolute_uri()
        canonical_path = self.request.path
        
        # Convert sr-latn URLs to sr for canonical
        if 'sr-latn' in canonical_path:
            canonical_path = canonical_path.replace('sr-latn', 'sr')
            
        canonical_url = self.request.build_absolute_uri(canonical_path)
            
        # Generate alternate URLs
        if 'sr-latn' in current_url:
            alternate_sr = current_url.replace('sr-latn', 'sr')
            alternate_lat = current_url
        else:
            alternate_sr = current_url
            alternate_lat = current_url.replace('sr', 'sr-latn')
            
        return {
            'canonical_url': canonical_url,
            'alternate_sr': alternate_sr,
            'alternate_lat': alternate_lat,
            'current_url': current_url,
        }