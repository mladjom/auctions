# views/category_views.py
from .base_view import BaseListView, BaseDetailView
from ..models import Category, Auction
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class CategoryListView(BaseListView):
    """View for listing categories"""
    model = Category
    template_name = 'auctions/category_list.html'
    ordering = 'title_sr'  # Order by Serbian title by default
    
    def get_queryset(self):
        """Get only root categories (no parent)"""
        return super().get_queryset().filter(parent__isnull=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add auction counts for each category
        categories = context['object_list']
        for category in categories:
            category.active_auction_count = Auction.objects.filter(
                category=category,
                is_active=True,
                end_time__gt=timezone.now()
            ).count()
        
        context.update({
            'meta_title': _('Categories | Auctions'),
            'meta_description': _('Browse auction categories'),
            'total_categories': self.model.objects.filter(is_active=True).count()
        })
        
        return context

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        
        # Add Categories level
        breadcrumbs.append({
            'title': _('Categories'),
            'url': None
        })
        
        return breadcrumbs

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class CategoryDetailView(BaseListView):
    model = Auction
    template_name = 'auctions/category_detail.html'
    ordering = 'end_time'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        return queryset.filter(category=self.category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'category': self.category,
            'meta_title': f"{self.category.title} | {_('Auctions')}",
            'meta_description': _('{category} auctions available').format(category=self.category.title),
            'active_auctions': self.get_queryset().filter(
                end_time__gt=timezone.now()
            ).count()
        })
        
        return context
        
    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        
        # Add Categories level
        breadcrumbs.append({
            'title': _('Categories'),
            'url': self.get_language_specific_url('auctions:category-list')
        })
        
        # Add current category
        breadcrumbs.append({
            'title': self.category.title,
            'url': None
        })
        
        return breadcrumbs


# @method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
# class CategoryDetailView(BaseDetailView):
#     model = Category
#     template_name = 'auctions/category_detail.html'
#     context_object_name = 'category'
#     slug_field = 'slug'
#     slug_url_kwarg = 'slug'
    
#     def get_navigation_objects(self):
#         """Override to sort categories alphabetically by title instead of by date"""
#         try:
#             queryset = self.get_queryset()
#             prev_obj = queryset.filter(
#                 title__lt=self.object.title
#             ).order_by('-title').first()
#             next_obj = queryset.filter(
#                 title__gt=self.object.title
#             ).order_by('title').first()
#             return prev_obj, next_obj
#         except:
#             return None, None

#     def get_related_objects(self, limit=4):
#         """Get active auctions from this category"""
#         try:
#             return Auction.objects.filter(
#                 category=self.object,
#                 is_active=True
#             ).order_by('-created_at')[:limit]
#         except:
#             return []

#     def get_schema_data(self):
#         """Generate Schema.org data for the category"""
#         category = self.object
#         schema = {
#             "@context": "https://schema.org",
#             "@type": "CollectionPage",
#             "name": category.title,
#             "description": category.description or '',
#             "breadcrumb": {
#                 "@type": "BreadcrumbList",
#                 "itemListElement": [
#                     {
#                         "@type": "ListItem",
#                         "position": 1,
#                         "name": _("Home"),
#                         "item": self.get_language_specific_url('home')
#                     },
#                     {
#                         "@type": "ListItem",
#                         "position": 2,
#                         "name": _("Categories"),
#                         "item": self.get_language_specific_url('auctions:category-list')
#                     },
#                     {
#                         "@type": "ListItem",
#                         "position": 3,
#                         "name": category.title
#                     }
#                 ]
#             }
#         }
#         return schema

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         category = self.object
#         active_auctions = Auction.objects.filter(
#             category=category,
#             is_active=True,  # The auction must be active
#         )
#         # Add category-specific meta tags
#         context.update({
#             'meta_title': _('{category_name} Auctions').format(
#                 category_name=category.meta_title
#             ),
#             'meta_description': category.meta_description[:160] if category.meta_description else '',
#             'breadcrumbs': [
#                 {
#                     'title': _('Home'),
#                     'url': self.get_language_specific_url('home')
#                 },
#                 {
#                     'title': _('Categories'),
#                     'url': self.get_language_specific_url('auctions:category-list')
#                 },
#                 {
#                     'title': category.title,
#                     'url': None
#                 }
#             ],
#             # Get all active auctions for this category
#             'object_list': Auction.objects.filter(
#                 category=category,
#                 is_active=True
#             ).order_by('-created_at'),
#             'og_type': 'website',  # Override article type from base
#             'active_auctions': active_auctions.count()

#         })
        
#         return context