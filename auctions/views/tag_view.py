from django.views.generic import DetailView
from ..models.tag_model import Tag

class TagDetailView(DetailView):
    model = Tag
    template_name = 'auctions/tag_detail.html'
    context_object_name = 'tag'
    slug_field = 'name'
    slug_url_kwarg = 'slug'
