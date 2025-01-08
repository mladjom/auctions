# auctions/admin/__init__.py
from .auction_admin import AuctionAdmin
from .category_admin import CategoryAdmin
from .executor_admin import ExecutorAdmin
from .location_admin import LocationAdmin
from .tag_admin import TagAdmin
from .document_admin import AuctionDocumentAdmin

from ..models import Auction, Category, Executor, Location, Tag, AuctionDocument

from django.contrib import admin

admin.site.register(Auction, AuctionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Executor, ExecutorAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(AuctionDocument, AuctionDocumentAdmin)