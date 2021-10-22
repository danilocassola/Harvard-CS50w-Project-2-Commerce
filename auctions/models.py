from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionCategories(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"


class AuctionListings(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    imageUrl = models.CharField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(AuctionCategories, on_delete=models.SET_DEFAULT, default="", blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_user")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"


class Bids(models.Model):
    listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="bids_listing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_user")
    #current_price = models.FloatField()
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.listing} - Current Price: {self.current_price}"


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_user")
    listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="comments_listing")
    comment = models.CharField(max_length=500)
    timepost = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment: {self.comment}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")
    listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="listing")

    def __str__(self):
        return f"{self.user} {self.listing}"