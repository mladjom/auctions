from celery import shared_task
from django.utils import timezone
from ..models.auction_model import Auction  # adjust import based on your model name

@shared_task
def update_auction_status():
    return Auction.objects.filter(
        is_active=True,
        end_time__lte=timezone.now()
    ).update(is_active=False)