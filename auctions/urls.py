# auctions/urls.py
from django.urls import path
from .views import (
    AuctionListView, AuctionDetailView,
    CategoryListView, CategoryDetailView,
    ExecutorListView, ExecutorDetailView,
    LocationListView, LocationDetailView,
    TagListView, TagDetailView
)

app_name = 'auctions'

urlpatterns = [
    # Auction URLs
    path('', AuctionListView.as_view(), name='auction-list'),
    path('auction/<slug:slug>/', AuctionDetailView.as_view(), name='auction-detail'),
    
    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Executor URLs
    path('executors/', ExecutorListView.as_view(), name='executor-list'),
    path('executor/<slug:slug>/', ExecutorDetailView.as_view(), name='executor-detail'),
    
    # Location URLs
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('location/<slug:slug>/', LocationDetailView.as_view(), name='location-detail'),
    
    # Tag URLs
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tag/<slug:slug>/', TagDetailView.as_view(), name='tag-detail'),
]