from django.views.generic import ListView, DetailView
from django.db.models import Q, F
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import json

class BreadcrumbMixin:
    def get_breadcrumbs(self):
        return [{'title': 'Home', 'url': '/'}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context

class MetaTagsMixin:
    def get_meta_title(self):
        if hasattr(self.object, 'meta_title'):
            return self.object.meta_title
        return ''

    def get_meta_description(self):
        if hasattr(self.object, 'meta_description'):
            return self.object.meta_description
        return ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = self.get_meta_title()
        context['meta_description'] = self.get_meta_description()
        return context

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class BaseListView(ListView, BreadcrumbMixin, MetaTagsMixin):
    """
    Base list view with pagination, filtering, breadcrumbs and meta tags
    """
    paginate_by = 3
    template_name = None
    context_object_name = 'objects'
    search_fields = []

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        search_query = self.request.GET.get('q')
        
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
        
        return queryset

    def get_context_data(self, **kwargs):
        # Start with context from superclasses (BreadcrumbMixin, MetaTagsMixin)
        context = super().get_context_data(**kwargs)
        
        # Add search query to context
        context['search_query'] = self.request.GET.get('q', '')
        
        # Add canonical URL for the current page
        canonical_path = self.request.path
        if 'sr-latn' in canonical_path:
            canonical_path = canonical_path.replace('sr-latn', 'sr')
        context['canonical_url'] = self.request.build_absolute_uri(canonical_path)
        
        # Add alternate URLs
        current_url = self.request.build_absolute_uri()
        if 'sr-latn' in current_url:
            context['alternate_sr'] = current_url.replace('sr-latn', 'sr')
            context['alternate_lat'] = current_url
        else:
            context['alternate_sr'] = current_url
            context['alternate_lat'] = current_url.replace('sr', 'sr-latn')
       

        
        return context

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class BaseDetailView(DetailView, BreadcrumbMixin, MetaTagsMixin):
    """
    Base detail view with breadcrumbs and meta tags
    """
    template_name = None
    context_object_name = 'objects'

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_previous_next_objects(self):
        try:
            queryset = self.get_queryset()
            previous_obj = queryset.filter(
                created_at__lt=self.object.created_at,
                is_active=True
            ).order_by('-created_at').first()
            
            next_obj = queryset.filter(
                created_at__gt=self.object.created_at,
                is_active=True
            ).order_by('created_at').first()
            
            return previous_obj, next_obj
        except:
            return None, None

    def get_related_objects(self):
        return self.model.objects.filter(
            is_active=True
        ).exclude(pk=self.object.pk)[:4]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Canonical and alternate URLs
        canonical_path = self.request.path
        if 'sr-latn' in canonical_path:
            canonical_path = canonical_path.replace('sr-latn', 'sr')
        context['canonical_url'] = self.request.build_absolute_uri(canonical_path)
        
        # Add alternate URLs
        current_url = self.request.build_absolute_uri()
        if 'sr-latn' in current_url:
            context['alternate_sr'] = current_url.replace('sr-latn', 'sr')
            context['alternate_lat'] = current_url
        else:
            context['alternate_sr'] = current_url
            context['alternate_lat'] = current_url.replace('sr', 'sr-latn')

        # Navigation and related
        prev_obj, next_obj = self.get_previous_next_objects()
        context.update({
            'previous_object': prev_obj,
            'next_object': next_obj,
            'related_objects': self.get_related_objects(),
            'schema_data': json.dumps(self.object.get_schema_data()),
            'meta_title': self.object.meta_title,
            'meta_description': self.object.meta_description,
            'og_title': self.object.meta_title,
            'og_description': self.object.meta_description,
            'og_type': 'article',
            'og_url': context['canonical_url'],
        })

        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not request.user.is_staff:
            self.object.increment_view_count()
        response['Last-Modified'] = self.object.updated_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response