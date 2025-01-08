# auctions/urls.py
from django.urls import path
from .views import (
    AuctionDetailView,
    TagDetailView,
    LocationDetailView,
    ExecutorDetailView,
    CategoryDetailView
)

urlpatterns = [
    path('auctions/<slug:slug>/', AuctionDetailView.as_view(), name='auction-detail'),
    path('tags/<slug:slug>/', TagDetailView.as_view(), name='tag-detail'),
    path('locations/<slug:slug>/', LocationDetailView.as_view(), name='location-detail'),
    path('executors/<slug:slug>/', ExecutorDetailView.as_view(), name='executor-detail'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
]