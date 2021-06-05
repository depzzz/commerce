from django.contrib import admin
from .models import User, listings, bids, comments, watchlist, winner

#For the sake of showing readonly_fields into django admin interface
class listingsread(admin.ModelAdmin):
    fields = ['id', 'title', 'description', 'owner', 'current_price', 'image_url', 'category', 'status', 'added_on', 'winner']
    readonly_fields = ['added_on','id']

class bidsread(admin.ModelAdmin):
    fields = ['id','user', 'listingid', 'bid_amount','last_modified']
    readonly_fields = ['id','last_modified']

class commentsread(admin.ModelAdmin):
    fields = ['id','user', 'listingid', 'comment', 'added_on']
    readonly_fields = ['id','added_on']

class watchlistread(admin.ModelAdmin):
    fields = ['id','user', 'listingid', 'added_on']
    readonly_fields = ['id','added_on']

class winnerread(admin.ModelAdmin):
    fields = ['id','winner', 'owner', 'listingid', 'title','bid_amount','timestamp']
    readonly_fields = ['id','timestamp']

class userread(admin.ModelAdmin):
    fields = ['id','username','is_superuser']
    readonly_fields = ['id','is_superuser']

# Register your models here.
admin.site.register(listings,listingsread)
admin.site.register(bids,bidsread)
admin.site.register(comments,commentsread)
admin.site.register(watchlist,watchlistread)
admin.site.register(winner,winnerread)
admin.site.register(User,userread)