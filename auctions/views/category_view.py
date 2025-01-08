from django.views.generic import DetailView
from ..models.category_model import Category

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'auctions/category_detail.html'
    context_object_name = 'category'
    slug_field = 'name'
    slug_url_kwarg = 'slug'
