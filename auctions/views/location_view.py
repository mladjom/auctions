# views/location_view.py
from .base_view import BaseListView, BaseDetailView
from ..models import Location, Auction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.utils.translation import gettext_lazy as _

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class LocationListView(BaseListView):
    """View for listing locations"""
    model = Location
    template_name = 'auctions/location_list.html'
    ordering = 'title_sr'  # Order by Serbian title by default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add auction counts for each location
        locations = context['object_list']
        for location in locations:
            location.active_auction_count = Auction.objects.filter(
                location=location,
                is_active=True,
            ).count()
        
        context.update({
            'meta_title': _('Locations | Auctions'),
            'meta_description': _('Browse auction locations'),
            'total_locations': self.model.objects.filter(is_active=True).count()
        })
        
        return context

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        
        # Add Locations level
        breadcrumbs.append({
            'title': _('Locations'),
            'url': None
        })
        
        return breadcrumbs

class LocationDetailView(BaseDetailView):
    model = Location
    template_name = 'auctions/location_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['auctions'] = Auction.objects.filter(
            location=self.object
        ).order_by('-start_time')
        return context
    
    def get_breadcrumbs(self):
        obj = self.get_object()
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Locations', 'url': '/locations/'},
            {'title': f"{obj.city}, {obj.municipality}", 'url': None}
        ]