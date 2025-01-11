# views/auction_view.py
from django.utils import timezone
from .base_view import BaseListView, BaseDetailView
from ..models import Auction

class AuctionListView(BaseListView):
    model = Auction
    template_name = 'auctions/auction_list.html'
    context_object_name = 'auctions'
    search_fields = ['title', 'description', 'code']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        location = self.request.GET.get('location')
        
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category__slug=category)
        if location:
            queryset = queryset.filter(location__slug=location)
            
        return queryset.order_by('end_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_auctions'] = self.model.objects.filter(
            end_time__gt=timezone.now()
        ).count()
        return context

class AuctionDetailView(BaseDetailView):
    model = Auction
    template_name = 'auctions/auction_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auction = self.get_object()
        
        context.update({
            'auction': auction,
            'meta_title': f"Auction: {auction.title}",
            'meta_description': auction.description[:160],
            'related_auctions': self.model.objects.filter(
                category=auction.category
            ).exclude(code=auction.code)[:3]
        })
        
        return context