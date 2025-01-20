# views/auction_view.py
from django.utils import timezone
from .base_view import BaseListView, BaseDetailView
from django.utils.translation import gettext_lazy as _, gettext
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from ..models import Auction, Category, Location
from django.db.models import Q
from django.utils.timezone import now

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class AuctionListView(BaseListView):
    model = Auction
    template_name = 'auctions/auction_list.html'
    ordering = 'end_time'
    
    def get_search_fields(self):
        """Get language-specific search fields"""
        fields = self.get_language_specific_fields()
        return [fields['title'], fields['description']]
        
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        filters = {
            'category__slug': self.request.GET.get('category'),
            'location__slug': self.request.GET.get('location')
        }
        filters = {k: v for k, v in filters.items() if v}
        if filters:
            queryset = queryset.filter(**filters)
            
        # Apply search
        search_query = self.request.GET.get('q')
        if search_query:
            search_fields = self.get_search_fields()
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        location_slug = self.request.GET.get('location')
        
        category = Category.objects.filter(slug=category_slug).first() if category_slug else None
        location = Location.objects.filter(slug=location_slug).first() if location_slug else None

        title_parts = [gettext('Auctions')]
        if search_query:
            title_parts.append(gettext('Search: {query}').format(query=search_query))
        if category:
            title_parts.append(str(category.title))
        if location:
            title_parts.append(str(location.title))

        # Get base active auctions queryset
        active_auctions = self.model.objects.filter(
            is_active=True
        ) 
               
        # Apply filters to active auctions count
        filters = {}
        if category:
            filters['category'] = category
        if location:
            filters['location'] = location
        
        if filters:
            active_auctions = active_auctions.filter(**filters)
        
        # Apply search to active auctions if exists
        if search_query:
            search_fields = self.get_search_fields()
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            active_auctions = active_auctions.filter(q_objects)        
               
        context.update({
            'meta_title': ' | '.join(title_parts),
            'meta_description': self.get_meta_description(category, search_query),
            'categories': Category.objects.filter(is_active=True),
            'locations': Location.objects.filter(is_active=True),
            'active_auctions': active_auctions.count()
        })
        
        return context
        
    def get_meta_description(self, category=None, search_query=None):
        parts = []
                
        location_slug = self.request.GET.get('location')
        if location_slug:
            location = Location.objects.filter(slug=location_slug).first()
            if location:
                parts.append(str(location.title))
        
        if category:
            parts.append(_('{category} auctions').format(category=category.title))
        else:
            parts.append(_('auctions'))
            
        if not search_query and not category and not location_slug:
            return _('Browse our latest auctions')
        
        if search_query:
            parts.append(_('Search results for {query}').format(query=search_query))   
                     
        return _('Browse {description}').format(description=' '.join(parts))

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        
        # Add Auctions level
        breadcrumbs.append({
            'title': _('Auctions'),
            'url': None
        })
        
        base_url = self.get_language_specific_url('auctions:auction-list')
        
        # Add category level if filtered
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                breadcrumbs[-1]['url'] = base_url
                breadcrumbs.append({
                    'title': category.title,
                    'url': None
                })

        # Add location level if filtered
        location_slug = self.request.GET.get('location')
        if location_slug:
            location = Location.objects.filter(slug=location_slug).first()
            if location:
                breadcrumbs[-1]['url'] = base_url
                breadcrumbs.append({
                    'title': location.title,
                    'url': None
                })
        
        # Add search level if searching
        search_query = self.request.GET.get('q')
        if search_query:
            breadcrumbs[-1]['url'] = base_url
            breadcrumbs.append({
                'title': search_query,
                'url': None
            })
        
        return breadcrumbs

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class AuctionDetailView(BaseDetailView):
    """Detail view for displaying auction information with related auctions and navigation."""
    model = Auction
    template_name = 'auctions/auction_detail.html'
    
    def get_queryset(self):
        """Optimize queryset with required related fields."""
        return (super().get_queryset()
                .select_related('category', 'location', 'executor')
                .filter(end_time__gt=timezone.now()))
    
    def get_navigation_objects(self):
        """Get previous and next auctions within the same category."""
        auction = self.object
        base_query = self.get_queryset().filter(category=auction.category)
        
        prev_obj = base_query.filter(
            end_time__lt=auction.end_time
        ).order_by('-end_time').first()
        
        next_obj = base_query.filter(
            end_time__gt=auction.end_time
        ).order_by('end_time').first()
        
        return prev_obj, next_obj
    
    def get_related_objects(self, limit=3):
        """Get related auctions from the same category."""
        return (self.get_queryset()
                .filter(category=self.object.category)
                .exclude(pk=self.object.pk)
                .order_by('?')[:limit])
    
    def get_meta_data(self):
        """Get meta information for SEO."""
        auction = self.object
        return {
            'meta_title': f"{auction.title} | {_('Auctions')}",
            'meta_description': auction.description[:160]
        }
    
    def get_context_data(self, **kwargs):
        """Extend context with auction-specific data."""
        context = super().get_context_data(**kwargs)
        context.update(self.get_meta_data())
        return context
    
    def get_breadcrumbs(self):
        """Generate breadcrumb navigation for auction detail page."""
        auction = self.object
        return [
            *super().get_breadcrumbs(),
            {
                'title': _('Auctions'),
                'url': self.get_language_specific_url('auctions:auction-list')
            },
            # {
            #     'title': auction.category.title,
            #     'url': self.get_language_specific_url(
            #         'auctions:category-detail',
            #         kwargs={'slug': auction.category.slug}
            #     )
            # },
            {
                'title': auction.title,
                'url': None
            }
        ]



# @method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
# class AuctionDetailView(BaseDetailView):
#     """Detail view for auctions with multilingual support"""
#     model = Auction
#     template_name = 'auctions/auction_detail.html'

#     def get_queryset(self):
#         """Get queryset with related objects"""
#         return (super().get_queryset()
#                 .select_related('category', 'location', 'executor')
#                 .prefetch_related('images', 'documents', 'tags'))

#     def get_context_data(self, **kwargs):
#         """Get context data with additional auction information"""
#         context = super().get_context_data(**kwargs)
        
#         # Get related auctions from same category
#         related_auctions = (
#             Auction.objects.filter(
#                 #category=self.object.category,
#                 status='CONFIRMED',
#                 #end_time__gt=timezone.now()
#             )
#             .exclude(pk=self.object.pk)
#             .order_by('-start_time')[:3]
#         )

#         context.update({
#             'related_auctions': related_auctions,
#             'meta_title': self.object.meta_title,
#             'meta_description': self.object.meta_description,
#             'og_type': 'product',
#             'og_title': self.object.meta_title,
#             'og_description': self.object.meta_description,
#         })

#         return context

#     def get_breadcrumbs(self):
#         """Get breadcrumbs for auction detail"""
#         breadcrumbs = super().get_breadcrumbs()
        
#         # Add Auctions level
#         breadcrumbs.append({
#             'title': _('Auctions'),
#             'url': self.get_language_specific_url('auctions:auction-list')
#         })
        
#         # Add current auction
#         breadcrumbs.append({
#             'title': self.object.title,
#             'url': None
#         })
        
#         return breadcrumbs