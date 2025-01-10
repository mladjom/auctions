# views/executor_view.py
from django.db.models import Count, Avg
from .base_view import BaseListView, BaseDetailView
from ..models import Executor, Auction

class ExecutorListView(BaseListView):
    model = Executor
    template_name = 'auctions/executor_list.html'
    context_object_name = 'executors'
    search_fields = ['name', 'jurisdiction']
    
    def get_queryset(self):
        return super().get_queryset().annotate(
            auction_count=Count('auction'),
            avg_price=Avg('auction__starting_price')
        )
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Executors', 'url': None}
        ]

class ExecutorDetailView(BaseDetailView):
    model = Executor
    template_name = 'auctions/executor_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_auctions'] = Auction.objects.filter(
            executor=self.object,
            status='active'
        )
        context['completed_auctions'] = Auction.objects.filter(
            executor=self.object,
            status='completed'
        )
        return context
    
    def get_breadcrumbs(self):
        obj = self.get_object()
        return [
            {'title': 'Home', 'url': '/'},
            {'title': 'Executors', 'url': '/executors/'},
            {'title': obj.name, 'url': None}
        ]
