# auctions/views/auction_views.py
from django.views.generic import DetailView
from ..models.auction_model import Auction

class AuctionDetailView(DetailView):
    model = Auction
    template_name = 'auctions/auction_detail.html'
    context_object_name = 'auction'
    slug_field = 'code'
    slug_url_kwarg = 'slug'