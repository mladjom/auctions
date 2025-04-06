# auctions/views/__init__.py
from .auction_view import AuctionDetailView, AuctionListView
from .tag_view import TagDetailView, TagListView
from .location_view import LocationDetailView, LocationListView
from .executor_view import ExecutorDetailView, ExecutorListView
from .category_view import CategoryDetailView, CategoryListView
from .home_view import HomeView

__all__ = [
    AuctionListView, AuctionDetailView,
    CategoryListView, CategoryDetailView,
    ExecutorListView, ExecutorDetailView,
    LocationListView, LocationDetailView,
    TagListView, TagDetailView,
    HomeView
]