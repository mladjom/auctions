from django.views.generic import ListView, DetailView
from django.db.models import Q, F
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import json
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.urls import reverse

class BreadcrumbMixin:
    """Mixin for handling multilingual breadcrumb navigation"""
    
    def get_language_specific_url(self, url_name, **kwargs):
        """Get language-specific URL"""
        if not url_name:
            return '/'
            
        current_language = get_language()
        url = reverse(url_name, kwargs=kwargs)
        
        # Add language code to URL if using sr-Latn
        if current_language == 'sr-Latn':
            return f'/sr-Latn{url}'
        return url

    def get_breadcrumbs(self):
        """Base method for breadcrumbs that handles language-specific URLs"""
        return [{
            'title': _('Home'),
            'url': self.get_language_specific_url('home')
        }]
    
class MetaTagsMixin:
    """Mixin for handling meta tags and SEO"""
    def get_meta_tags(self):
        """Override this method to provide custom meta tags"""
        meta = {
            'title': getattr(self.object, 'meta_title', ''),
            'description': getattr(self.object, 'meta_description', ''),
        }
        return meta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meta_tags = self.get_meta_tags()
        context.update(meta_tags)
        return context

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

        
@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class BaseListView(ListView, BreadcrumbMixin, MetaTagsMixin, URLHandlerMixin):
    """Base list view with common functionality"""
    paginate_by = 3
    search_fields = []
    ordering = '-created_at'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        
        # Handle search
        search_query = self.request.GET.get('q')
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
            
        return queryset.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_query': self.request.GET.get('q', ''),
            **self.get_url_variants()
        })
        return context

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class BaseDetailView(DetailView, BreadcrumbMixin, MetaTagsMixin, URLHandlerMixin):
    """Base detail view with common functionality"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_navigation_objects(self):
        """Get previous and next objects"""
        try:
            queryset = self.get_queryset()
            prev_obj = queryset.filter(
                created_at__lt=self.object.created_at
            ).order_by('-created_at').first()
            next_obj = queryset.filter(
                created_at__gt=self.object.created_at
            ).order_by('created_at').first()
            return prev_obj, next_obj
        except:
            return None, None

    def get_related_objects(self, limit=4):
        """Get related objects based on model and current object"""
        try:
            return self.model.objects.filter(
                is_active=True
            ).exclude(pk=self.object.pk)[:limit]
        except:
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ensure URL variants are added to context
        context.update(self.get_url_variants())
        
        # Get schema data if available
        schema_data = getattr(self.object, 'get_schema_data', lambda: {})()
        
        # Get navigation objects
        prev_obj, next_obj = self.get_navigation_objects()
        
        context.update({
            'previous_object': prev_obj,
            'next_object': next_obj,
            'related_objects': self.get_related_objects(),
            'schema_data': json.dumps(schema_data),
            'og_title': getattr(self.object, 'meta_title', getattr(self.object, 'title', '')),
            'og_description': getattr(self.object, 'meta_description', ''),
            'og_type': 'article',
        })
        
        return context
