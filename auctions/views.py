from django.views.generic import DetailView
from .models.auction_model import Auction
from .models.tag_model import Tag
from .models.location_model import Location
from .models.executor_model import Executor
from .models.category_model import Category

class AuctionDetailView(DetailView):
    model = Auction
    template_name = 'auctions/auction_detail.html'
    context_object_name = 'auction'
    slug_field = 'code'  # Use code instead of slug
    slug_url_kwarg = 'slug'  # Keep the URL parameter name as slug

class TagDetailView(DetailView):
    model = Tag
    template_name = 'auctions/tag_detail.html'
    context_object_name = 'tag'

class LocationDetailView(DetailView):
    model = Location
    template_name = 'auctions/location_detail.html'
    context_object_name = 'location'

class ExecutorDetailView(DetailView):
    model = Executor
    template_name = 'auctions/executor_detail.html'
    context_object_name = 'executor'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'auctions/category_detail.html'
    context_object_name = 'category'
