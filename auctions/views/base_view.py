# views/base_view.py
from django.views.generic import ListView, DetailView
from django.db.models import Q, F
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import json
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.urls import reverse
from .mixins_view import SchemaMixin, SEOMixin, LanguageAwareMixin, URLHandlerMixin

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
    
@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class BaseListView(ListView, LanguageAwareMixin, SchemaMixin, SEOMixin, URLHandlerMixin):
    """Base list view with common functionality"""
    paginate_by = 3

    def get_queryset(self):
        """Get base queryset with search support"""
        queryset = super().get_queryset()
        
        # Check if model has is_active field before filtering
        if any(f.name == 'is_active' for f in self.model._meta.fields):
            queryset = queryset.filter(is_active=True)
            
        search_query = self.request.GET.get('q')
        
        if search_query and hasattr(self, 'get_search_fields'):
            search_fields = self.get_search_fields()
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
        
        return queryset.order_by(self.ordering)
    
    def get_context_data(self, **kwargs):
        """Get context data with schema support"""
        context = super().get_context_data(**kwargs)
        breadcrumbs = self.get_breadcrumbs()
        
        # Add URL variants to context
        context.update(self.get_url_variants())
        
        # Convert LazyString objects to strings in schema data
        schema_data = {
            'page': self.get_list_schema(context['object_list']),
            'breadcrumbs': self.get_breadcrumb_schema(breadcrumbs),
        }
        schema_data = json.dumps(schema_data, default=str)
        
        context.update({
            'breadcrumbs': breadcrumbs,
            'schema_data': schema_data,
        })
        
        return context

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class BaseDetailView(DetailView, LanguageAwareMixin, SchemaMixin, SEOMixin, URLHandlerMixin):
    """Base detail view with common functionality"""

    def get_queryset(self):
        """Get base queryset with active filter"""
        queryset = super().get_queryset()
        
        # Check if model has is_active field before filtering
        if any(f.name == 'is_active' for f in self.model._meta.fields):
            queryset = queryset.filter(is_active=True)
            
        return queryset

    def get_context_data(self, **kwargs):
        """Get context data with schema support"""
        context = super().get_context_data(**kwargs)
        breadcrumbs = self.get_breadcrumbs()
        
        # Add URL variants to context
        context.update(self.get_url_variants())
        
        # Increment view count
        if hasattr(self.object, 'increment_view_count'):
            self.object.increment_view_count()
        
        # Convert LazyString objects to strings in schema data
        schema_data = {
            'page': self.get_detail_schema(self.object),
            'breadcrumbs': self.get_breadcrumb_schema(breadcrumbs),
        }
        schema_data = json.dumps(schema_data, default=str)
        
        context.update({
            'breadcrumbs': breadcrumbs,
            'schema_data': schema_data,
        })
        
        return context