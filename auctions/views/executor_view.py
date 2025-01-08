from django.views.generic import DetailView
from ..models.executor_model import Executor

class ExecutorDetailView(DetailView):
    model = Executor
    template_name = 'auctions/executor_detail.html'
    context_object_name = 'executor'
    slug_field = 'name'
    slug_url_kwarg = 'slug'
