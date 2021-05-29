from django.contrib import admin
from .models import listings, bids, comments, watchlist, winner

# Register your models here.
admin.site.register(listings)
admin.site.register(bids)
admin.site.register(comments)
admin.site.register(watchlist)
admin.site.register(winner)
