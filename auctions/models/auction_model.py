from django.db import models
from django.utils.translation import gettext_lazy as _
from .base_model import BaseModel
from .category_model import Category
from .tag_model import Tag
from .executor_model import Executor
from .location_model import Location
from .image_model import Image
from .auction_document_model import AuctionDocument
from django.urls import reverse

class Auction(BaseModel):
    STATUS_CHOICES = [
        ('CONFIRMATION_IN_PROGRESS', _('Потврђивање у току')),
        ('CONFIRMED', _('Потврђено')),
        ('EXPIRED', _('Истекло')),
    ]

    # Basic information
    code = models.CharField(_("Code"), max_length=20, primary_key=True)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='CONFIRMATION_IN_PROGRESS',
        verbose_name=_('Status')
    )
    url = models.URLField(_("URL"))

    # Dates
    publication_date = models.DateTimeField(_("Publication Date"))
    start_time = models.DateTimeField(_("Start Time"))
    end_time = models.DateTimeField(_("End Time"))

    # Pricing
    starting_price = models.DecimalField(
        _("Starting Price"), 
        max_digits=10, 
        decimal_places=2
    )
    estimated_value = models.DecimalField(
        _("Estimated Value"), 
        max_digits=10, 
        decimal_places=2
    )
    bidding_step = models.DecimalField(
        _("Bidding Step"), 
        max_digits=10, 
        decimal_places=2
    )

    # Additional Info
    sale_number = models.CharField(_("Sale Number"), max_length=50)

    # Relations
    location = models.ForeignKey(
        Location,
        verbose_name=_("Location"),
        on_delete=models.CASCADE,
        related_name='auctions'
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.SET_NULL,
        null=True,
        related_name='auctions'
    )
    executor = models.ForeignKey(
        Executor,
        verbose_name=_("Executor"),
        on_delete=models.SET_NULL,
        null=True,
        related_name='auctions'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_("Tags"),
        blank=True,
        related_name='auctions'
    )
    images = models.ManyToManyField(
        Image,
        verbose_name=_("Images"),
        blank=True,
        related_name='auctions'
    )
    documents = models.ManyToManyField(
        AuctionDocument,
        verbose_name=_("Documents"),
        blank=True,
        related_name='auctions'
    )

    view_count = None

    class Meta:
        verbose_name = _("Auction")
        verbose_name_plural = _("Auctions")
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_time']),
            models.Index(fields=['publication_date']),
        ]

    def __str__(self):
        return f"{self.code} - {self.title_sr}"

    # def is_active(self):
    #     return self.status == 'CONFIRMED'

    def get_absolute_url(self):
        return reverse('auctions:auction-detail', args=[str(self.slug)])