from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORIES = (
    ('Asian', 'Asian'),
    ('European', 'European'),
    ('GlutenFree', 'Gluten Free'),
    ('Low Fat', 'Low Fat'),
    ('Keto', 'Keto'),
    ('Others', 'Others'),
)

class User(AbstractUser):
    location = models.CharField(max_length=255, default = "")

class Bid(models.Model):
    time = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user} put a bid in for {self.price}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_coms")
    title = models.CharField(max_length=25, default="")
    comment = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.user}: {self.comment}"


class Listing(models.Model):
    item = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=1000, choices=CATEGORIES, default=CATEGORIES[5][1])
    time = models.DateTimeField(auto_now_add=True, blank=True)
    closed = models.BooleanField(default=False)
    address = models.CharField(max_length=1000, default="")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owners")
    bids = models.ManyToManyField(Bid, blank=True, related_name="bids")
    comments = models.ManyToManyField(Comment, blank=True, related_name="comments")
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f"{self.item}: is {self.price} and is being sold by {self.owner}"


class watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listings")

    def __str__(self):
        return f"{self.user.username} listed {self.listing.id}"


class Data(models.Model):
    date = models.DateField(blank=False)
    inventory = models.IntegerField(default = 0)
    leftover = models.IntegerField(default = 0)
    sold = models.IntegerField(default = 0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_owner", default="")

    