from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

# Listing model
class Listing(models.Model):
    user = models.ForeignKey(User, related_name="listings", on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="won_listings")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")


    def __str__(self):
        return f"{self.id} - {self.user.username} - {self.title}"
    
    @property
    def highest_bidder(self):
        if self.current_bid is not None:
            highest_bid = self.bids.filter(bid_amount=self.current_bid).first()
            return highest_bid.user if highest_bid else "No bids yet"
        return None


# Bids model
class Bid(models.Model):
    user = models.ForeignKey(User, related_name="bids", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="bids", on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title} - {self.bid_amount}"



# Comments model
class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="comments", on_delete=models.CASCADE)
    comment_text = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.listing.title} - {self.comment_text}"

# Watchlist model
class Watchlist(models.Model):
    user = models.ForeignKey(User, related_name="watchlists", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="watchlists", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"