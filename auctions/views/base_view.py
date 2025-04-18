# views/base_view.py
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import json
from django.utils.translation import gettext_lazy as _
from .mixins_view import SchemaMixin, SEOMixin, LanguageAwareMixin, URLHandlerMixin

    
@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class BaseListView(ListView, LanguageAwareMixin, SchemaMixin, SEOMixin, URLHandlerMixin):
    """Base list view with common functionality"""
    paginate_by = 12
    ordering = None

    def get_queryset(self):
        """Get base queryset with search support"""
        queryset = super().get_queryset()
        
        # Check if model has is_active field before filtering
        if any(f.name == 'is_active' for f in self.model._meta.fields):
            queryset = queryset.filter(is_active=True)
        
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
        
        prev_obj, next_obj = self.get_navigation_objects()
        
        context.update({
            'breadcrumbs': breadcrumbs,
            'schema_data': schema_data,
            'previous_object': prev_obj,
            'next_object': next_obj,
            'related_objects': self.get_related_objects()
        })
        
        return context
    
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
        """Get related objects"""
        try:
            return self.model.objects.filter(
                is_active=True
            ).exclude(pk=self.object.pk)[:limit]
        except:
            return []