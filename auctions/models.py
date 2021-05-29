from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.aggregates import Max


class User(AbstractUser):
    pass

STATUS_CHOICES = (
    ("O", "Open"),
    ("C", "Closed"),
)

CATEGORIES = (
    ("ENTERTAINMENT", "Entertainment"),
    ("ELECTRONICS", "Electronics"),
    ("FASHION", "Fashion"),
    ("GENERAL", "General"),
    ("HOME", "Home"),
    ("TOYS", "Toys"),
)

# Model for Listing Information (Create Listing)
class listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=250)
    owner = models.CharField(max_length=64)
    starting_price = models.PositiveIntegerField()
    image_url = models.URLField(max_length=200)

    category = models.CharField(max_length=13,
                            choices=CATEGORIES,
                            default='GENERAL')

    status = models.CharField(max_length=1,
                            choices=STATUS_CHOICES,
                            default='O')
    
    added_on = models.DateTimeField(auto_now_add=True)

# Model For Bids Placement (Place Bid)
class bids(models.Model):
    user = models.CharField(max_length=64)
    listingid = models.PositiveIntegerField()
    title = models.CharField(max_length=64)
    bid_amount = models.PositiveIntegerField()
    last_modified = models.DateTimeField(auto_now=True)

# Model For User Comments (Add a Comment)
class comments(models.Model):
    user = models.CharField(max_length=64)
    listingid = models.PositiveIntegerField()
    comment = models.CharField(max_length=500)
    added_on = models.DateTimeField(auto_now_add=True)

# Model For User Watchlist (Add to Watchlist)
class watchlist(models.Model):
    user = models.CharField(max_length=64)
    listingid = models.PositiveIntegerField()
    added_on = models.DateTimeField(auto_now_add=True)

# Model For Winner
class winner(models.Model):
    winner = models.CharField(max_length=64)
    owner = models.CharField(max_length=64)
    listingid = models.PositiveIntegerField()
    title = models.CharField(max_length=64)
    bid_amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)