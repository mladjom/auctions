from django.views.generic import DetailView
from ..models.location_model import Location

class LocationDetailView(DetailView):
    model = Location
    template_name = 'auctions/location_detail.html'
    context_object_name = 'location'
    slug_field = 'name'
    slug_url_kwarg = 'slug'
