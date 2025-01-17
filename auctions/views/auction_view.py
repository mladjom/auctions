# views/auction_view.py
from django.utils import timezone
from .base_view import BaseListView, BaseDetailView
from django.utils.translation import gettext_lazy as _, gettext
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from ..models import Auction, Category, Location
from django.db.models import Q, F

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class AuctionListView(BaseListView):
    model = Auction
    template_name = 'auctions/auction_list.html'
    ordering = 'end_time'
    
    def get_search_fields(self):
        """Get search fields based on current language"""
        if self.request.LANGUAGE_CODE == 'sr':
            return ['title_sr', 'description_sr']
        return ['title_lat', 'description_lat']  # Default to Latin for sr-Latn
        
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters
        filters = {
            'category__slug': self.request.GET.get('category'),
            'location__slug': self.request.GET.get('location')
        }
        
        # Apply non-empty filters
        filters = {k: v for k, v in filters.items() if v}
        if filters:
            queryset = queryset.filter(**filters)
            
        
        # Apply search query
        search_query = self.request.GET.get('q')
        search_fields = self.get_search_fields()
        if search_query and search_fields:
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter values for meta info
        context['categories'] = Category.objects.filter(is_active=True)
        context['locations'] = Location.objects.filter(is_active=True)
        search_query = self.request.GET.get('q')
        
        # Get category and location objects if they're being filtered
        category = None
        location = None
            
        # Build meta title based on filters
        title_parts = []
        if search_query:
            title_parts.append(_('Search: {query}').format(query=search_query))
        if category:
            title_parts.append(category.title)
        if location:
            title_parts.append(location.title)
        
        meta_title = ' | '.join(filter(None, [
            gettext('Auctions'),
            *title_parts
        ]))
        
        # Build meta description
        meta_description = _('Browse our latest auctions')
        if category:
            meta_description = _('{category} auctions available').format(category=category.title)
        if location:
            meta_description = _('Auctions in {location}').format(location=location.title)
        if search_query:
            meta_description = _('Search results for {query}').format(query=search_query)
            
        # Build breadcrumbs based on filters
        breadcrumbs = [
            {'title': _('Home'), 'url': self.get_language_specific_url('home')},
            {'title': _('Auctions'), 'url': None}
        ]
        
        if category:
            breadcrumbs[-1]['url'] = self.get_language_specific_url('auctions:auction-list')
            breadcrumbs.append({
                'title': category.title,
                'url': None
            })
        
        if location:
            breadcrumbs[-1]['url'] = self.get_language_specific_url('auctions:auction-list')
            breadcrumbs.append({
                'title': location.title,
                'url': None
            })
            
        if search_query:
            breadcrumbs[-1]['url'] = self.get_language_specific_url('auctions:auction-list')
            breadcrumbs.append({
                'title': _('Search Results'),
                'url': None
            })
            
        context.update({
            'meta_title': meta_title,
            'meta_description': meta_description,
            'breadcrumbs': breadcrumbs,
            'active_auctions': self.model.objects.filter(
                end_time__gt=timezone.now()
            ).count(),
            'og_type': 'website',
            'og_title': meta_title,
            'og_description': meta_description,
        })
        
        context['active_auctions'] = self.model.objects.filter(
            end_time__gt=timezone.now()
        ).count()        
        
        return context

class AuctionDetailView(BaseDetailView):
    model = Auction
    template_name = 'auctions/auction_detail.html'
    context_object_name = 'auction'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_related_objects(self, limit=3):
        """Override to get related auctions from same category"""
        return self.model.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(pk=self.object.pk)[:limit]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auction = self.object
        
        # Updated breadcrumbs with language-specific URLs
        context.update({
            'meta_title': f"Auction: {auction.title}",
            'meta_description': auction.description[:160] if auction.description else '',
            'related_auctions': self.get_related_objects(),
            'breadcrumbs': [
                {
                    'title': _('Home'),
                    'url': self.get_language_specific_url('home')
                },
                {
                    'title': _('Auctions'),
                    'url': self.get_language_specific_url('auctions:auction-list')
                },
                {
                    'title': auction.title,
                    'url': None
                }
            ]
        })
        
        return context