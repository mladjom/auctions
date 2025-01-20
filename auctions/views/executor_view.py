# views/executor_view.py
from .base_view import BaseListView, BaseDetailView
from ..models import Executor, Auction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class ExecutorListView(BaseListView):
    """View for listing executors"""
    model = Executor
    template_name = 'auctions/executor_list.html'
    ordering = 'title_sr'  # Order by Serbian title by default

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add auction counts for each executor
        executors = context['object_list']
        for executor in executors:
            executor.active_auction_count = Auction.objects.filter(
                executor=executor,
                is_active=True,
            ).count()
        
        context.update({
            'meta_title': _('Executors| Auctions'),
            'meta_description': _('Browse auction executors'),
            'total_executors': self.model.objects.filter(is_active=True).count()
        })
        
        return context

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        
        # Add Executorslevel
        breadcrumbs.append({
            'title': _('Executors'),
            'url': None
        })
        
        return breadcrumbs

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
