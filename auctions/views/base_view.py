# views/base_view.py
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from django.db.models import Q

class BreadcrumbMixin:
    """
    Mixin to add breadcrumbs to any view
    """
    breadcrumb_template = "components/breadcrumbs.html"

    def get_breadcrumbs(self):
        """
        Return a list of breadcrumb items in format:
        [{'title': 'Home', 'url': '/'}, {'title': 'Current', 'url': None}]
        """
        return [{'title': 'Home', 'url': '/'}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context

class MetaTagsMixin:
    """
    Mixin to add meta tags for SEO
    """
    def get_meta_title(self):
        return getattr(self, 'meta_title', '')
    
    def get_meta_description(self):
        return getattr(self, 'meta_description', '')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = self.get_meta_title()
        context['meta_description'] = self.get_meta_description()
        return context

class BaseListView(ListView, BreadcrumbMixin, MetaTagsMixin):
    """
    Base list view with pagination, filtering,  breadcrumbs and meta tags
    """
    paginate_by = 12
    template_name = None
    context_object_name = 'objects'
    search_fields = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
            
        return queryset
    
class BaseDetailView(DetailView, BreadcrumbMixin, MetaTagsMixin):
    """
    Base detail view with breadcrumbs and meta tags
    """
    template_name = None
    context_object_name = 'object'