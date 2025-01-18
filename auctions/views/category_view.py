# views/category_views.py
from django.db.models import Count
from .base_view import BaseListView, BaseDetailView
from ..models import Category, Auction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, F
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
        
        # Add category stats
        categories = context['object_list']
        stats = {}
        now = timezone.now()
        
        # Count total active categories
        total_categories = categories.count()
        
        for category in categories:
            base_query = category.auctions.filter(status='CONFIRMED')
            active_auctions = base_query.filter(
                start_time__lte=now,
                end_time__gt=now
            ).count()
            
            stats[category.pk] = {
                'total_auctions': base_query.count(),
                'active_auctions': active_auctions,
                'subcategories': category.children.filter(is_active=True).count()
            }
            # Add auction count directly to category object for template use
            category.auction_count = active_auctions
        
        context.update({
            'meta_title': _('Auction Categories'),
            'meta_description': _('Browse all auction categories'),
            'category_stats': stats,
            'total_categories': total_categories
        })
        
        return context

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class CategoryDetailView(BaseDetailView):
    model = Category
    template_name = 'auctions/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_navigation_objects(self):
        """Override to sort categories alphabetically by title instead of by date"""
        try:
            queryset = self.get_queryset()
            prev_obj = queryset.filter(
                title__lt=self.object.title
            ).order_by('-title').first()
            next_obj = queryset.filter(
                title__gt=self.object.title
            ).order_by('title').first()
            return prev_obj, next_obj
        except:
            return None, None

    def get_related_objects(self, limit=4):
        """Get active auctions from this category"""
        try:
            return Auction.objects.filter(
                category=self.object,
                is_active=True
            ).order_by('-created_at')[:limit]
        except:
            return []

    def get_schema_data(self):
        """Generate Schema.org data for the category"""
        category = self.object
        schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": category.title,
            "description": category.description or '',
            "breadcrumb": {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": _("Home"),
                        "item": self.get_language_specific_url('home')
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": _("Categories"),
                        "item": self.get_language_specific_url('auctions:category-list')
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": category.title
                    }
                ]
            }
        }
        return schema

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        
        # Add category-specific meta tags
        context.update({
            'meta_title': _('{category_name} Auctions').format(
                category_name=category.meta_title
            ),
            'meta_description': category.meta_description[:160] if category.meta_description else '',
            'breadcrumbs': [
                {
                    'title': _('Home'),
                    'url': self.get_language_specific_url('home')
                },
                {
                    'title': _('Categories'),
                    'url': self.get_language_specific_url('auctions:category-list')
                },
                {
                    'title': category.title,
                    'url': None
                }
            ],
            # Get all active auctions for this category
            'auctions': Auction.objects.filter(
                category=category,
                is_active=True
            ).order_by('-created_at'),
            'og_type': 'website'  # Override article type from base
        })
        
        return context