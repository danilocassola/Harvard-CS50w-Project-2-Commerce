from django.contrib import admin

from .models import User, AuctionCategories, AuctionListings, Bids, Comments, Watchlist

# Register your models here.
class AuctionListingsAdmin(admin.ModelAdmin):
	list_display = ("title", "category", "starting_bid", "active", "user")

class AuctionCategoriesAdmin(admin.ModelAdmin):
    list_display = ("id", "category",)

class BidsAdmin(admin.ModelAdmin):
    list_display = ("listing", "current_price", "user",)

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "comment",)

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "listing",)

admin.site.register(User)
admin.site.register(AuctionCategories, AuctionCategoriesAdmin)
admin.site.register(AuctionListings, AuctionListingsAdmin)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Watchlist, WatchlistAdmin)