from django.utils import timezone
from .base_view import BaseListView, BaseDetailView
from django.utils.translation import gettext_lazy as _, gettext
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from ..models import Auction, Category, Location
from django.db.models import Q
from django.utils.timezone import now

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class HomeView(BaseListView):
    model = Auction
    template_name = 'auctions/auction_list.html'
    ordering = 'end_time'