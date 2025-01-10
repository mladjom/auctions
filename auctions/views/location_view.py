# views/location_view.py
from django.db.models import Count
from .base_view import BaseListView, BaseDetailView
from ..models import Location, Auction

class LocationListView(BaseListView):
    model = Location
    template_name = 'auctions/location_list.html'
    context_object_name = 'locations'
    search_fields = ['municipality', 'city']
    
    def get_queryset(self):
        return super().get_queryset().annotate(
            auction_count=Count('auction')
        )
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Locations', 'url': None}
        ]

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