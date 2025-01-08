# auctions/views/__init__.py
from .auction_view import AuctionDetailView
from .tag_view import TagDetailView
from .location_view import LocationDetailView
from .executor_view import ExecutorDetailView
from .category_view import CategoryDetailView

__all__ = [
    'AuctionDetailView',
    'TagDetailView',
    'LocationDetailView',
    'ExecutorDetailView',
    'CategoryDetailView',
]