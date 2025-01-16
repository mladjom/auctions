# views/category_views.py
from django.db.models import Count
from .base_view import BaseListView, BaseDetailView
from ..models import Category, Auction

class CategoryListView(BaseListView):
    model = Category
    template_name = 'auctions/category_list.html'
    search_fields = ['title', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(auction_count=Count('auctions'))

    def get_breadcrumbs(self):
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Categories', 'url': None}
        ]

class CategoryDetailView(BaseDetailView):
    model = Category
    template_name = 'auctions/category_detail.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auctions = Auction.objects.filter(category=self.object).order_by('-created_at')
        context['auctions'] = auctions[:self.paginate_by]
        return context

    def get_breadcrumbs(self):
        obj = self.get_object()
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Categories', 'url': '/categories/'},
            {'title': obj.title, 'url': None}
        ]