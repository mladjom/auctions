# views/tag_view.py
from django.db.models import Count
from .base_view import BaseListView, BaseDetailView
from ..models import Tag, Auction

class TagListView(BaseListView):
    model = Tag
    template_name = 'auctions/tag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        return super().get_queryset().annotate(
            auction_count=Count('auction')
        )
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Tags', 'url': None}
        ]

class TagDetailView(BaseDetailView):
    model = Tag
    template_name = 'auctions/tag_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['auctions'] = Auction.objects.filter(
            tags=self.object
        ).order_by('-created_at')
        return context
    
    def get_breadcrumbs(self):
        obj = self.get_object()
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Tags', 'url': '/tags/'},
            {'title': obj.name, 'url': None}
        ]