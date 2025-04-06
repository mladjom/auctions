from django.views.generic import ListView, DetailView
from .models import PageModel


class PageListView(ListView):
    model = PageModel
    template_name = "pages/page_list.html"
    context_object_name = "pages"
    queryset = PageModel.objects.filter(is_published=True)


class PageDetailView(DetailView):
    model = PageModel
    template_name = "pages/page_detail.html"
    context_object_name = "page"

    def get_queryset(self):
        """Filter only active pages."""
        return PageModel.objects.filter(is_published=True)