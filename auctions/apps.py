from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AuctionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auctions'
    verbose_name = _('Auctions')
    
    def ready(self):
        import auctions.tasks  # This ensures tasks are registered
        import auctions.signals  # Keep your existing signals import if you have one