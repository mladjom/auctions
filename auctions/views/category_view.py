# views/category_view.py
from django.db.models import Count
from .base_view import BaseListView, BaseDetailView
from ..models import Category, Auction

class CategoryListView(BaseListView):
    model = Category
    template_name = 'auctions/category_list.html'
    context_object_name = 'categories'
    search_fields = ['name', 'description']  # Add search fields
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(
            auction_count=Count('auctions')
        )
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Categories', 'url': None}
        ]

class CategoryDetailView(BaseDetailView):
    model = Category
    template_name = 'auctions/category_detail.html'
    paginate_by = 12  # Same as BaseListView
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get auctions with pagination
        page = self.request.GET.get('page')
        auctions = Auction.objects.filter(
            category=self.object
        ).order_by('-created_at')
        
        # Create paginator
        from django.core.paginator import Paginator
        paginator = Paginator(auctions, self.paginate_by)
        auction_page = paginator.get_page(page)
        
        context['auctions'] = auction_page
        context['is_paginated'] = auction_page.has_other_pages()
        context['page_obj'] = auction_page
        
        return context
    
    def get_breadcrumbs(self):
        obj = self.get_object()
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Categories', 'url': '/categories/'},
            {'title': obj.name, 'url': None}
        ]