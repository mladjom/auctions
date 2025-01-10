# views/category_view.py
from django.db.models import Count
from .base_view import BaseListView, BaseDetailView
from ..models import Category, Auction

class CategoryListView(BaseListView):
    model = Category
    template_name = 'auctions/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return super().get_queryset().annotate(
            auction_count=Count('auction')
        )
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Categories', 'url': None}
        ]

class CategoryDetailView(BaseDetailView):
    model = Category
    template_name = 'auctions/category_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['auctions'] = Auction.objects.filter(
            category=self.object
        ).order_by('-created_at')
        return context
    
    def get_breadcrumbs(self):
        obj = self.get_object()
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Categories', 'url': '/categories/'},
            {'title': obj.name, 'url': None}
        ]