from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import *

class Message():
    def __init__(self, message, color):
        self.message = message
        self.color = color

class NewListing(forms.Form):
    title = forms.CharField(label="Title", max_length=64)
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={
        'rows': 20,
        'cols': 80,
        'placeholder': 'Enter the content here...',
        'class': 'form-control'
    }))
    starting_bid = forms.DecimalField(label="Starting Bid", max_digits=10, decimal_places=2)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Category", widget=forms.Select)
    image_url = forms.CharField(label="Image URL", required=False, widget=forms.TextInput(attrs={
        'placeholder': 'https://'
    }))

class NewCommentForm(forms.Form):
    comment_text = forms.CharField(label="Comment", widget=forms.Textarea(attrs={
        'rows': 20,
        'cols': 80,
        'placeholder': 'Enter the content here...',
        'class': 'form-control'
    }))

class NewBidForm(forms.Form):
    bid_amount = forms.DecimalField(label="", max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter your bid'
        }))


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "message": request.GET.get("a")
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url="login")
def add_listing_view(request):
    if request.method == "POST":
        form = NewListing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            starting_bid = form.cleaned_data["starting_bid"]
            user = request.user
            image_url = form.cleaned_data["image_url"]
            new_listing = Listing(title=title, description=description, category=category, starting_bid=starting_bid,current_bid=starting_bid, user=user, image_url=image_url)
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/add_listing.html", {
                "form": form
            })
    return render(request, "auctions/add_listing.html",{
        "form": NewListing()
    })

def listing_view(request, listing_id):
    message = None
    watchlist_status = None

    if request.GET.get("a"):
        watchlist_status= Message("Listing added to watchlist", "green") if request.GET.get("a") == 'Listing added to watchlist' else Message("Listing is already in the watchlist", "red")
    if request.GET.get("m"):
        message = Message("Bid Successfully Placed", "green") if request.GET.get("m") == 'SnmbuiMJPIKlrSq68NTstBWfLCHhMmiPq6lgKoqFM' else Message("Desired amount invalid", "red")
    
    listing = Listing.objects.get(pk=listing_id)
    bids = Bid.objects.filter(listing=listing)
    if not bids:
        listing.current_bid = listing.starting_bid
        listing.save()
    highest_bidder = listing.highest_bidder

    if request.method == "POST":
        ## ------ New code
        if "close_listing" in request.POST and request.user == listing.user and listing.active:
            listing.active = False
            listing.winner = highest_bidder
            listing.save()
            watchlist_status = Message("Auction closed successfully", "green")
        else:
            form = NewCommentForm(request.POST)
            if form.is_valid():
                comment_text = form.cleaned_data["comment_text"]
                user = request.user
                listing = Listing.objects.get(pk=listing_id)
                new_comment = Comment(comment_text=comment_text, user=user, listing=listing)
                new_comment.save()
                return HttpResponseRedirect(reverse("listing", args={listing_id:listing_id}))
            else:
                return render(request, "auctions/listing.html", {
                    "listing": Listing.objects.get(pk=listing_id),
                    "comments": Listing.objects.get(pk=listing_id).comments.all(),
                    "highest_bidder": highest_bidder,
                    "watchlist_status": watchlist_status,
                    "message": message,
                    "bid_form": NewBidForm(),
                    "comment_form": form,
                })
    winner_message = None
    if not listing.active and highest_bidder == request.user:
        winner_message = "Congratulations! You have won this auction."
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.comments.all(),
        "highest_bidder": highest_bidder,
        "watchlist_status": watchlist_status,
        "message": message,
        "winner_message": winner_message,
        "bid_form": NewBidForm(),
        "comment_form": NewCommentForm()
    })

@login_required(login_url="login")
def update_bid(request, listing_id):
    if request.method == "POST":
        form = NewBidForm(request.POST)
        if form.is_valid():
            placed_bid = form.cleaned_data["bid_amount"]
            listing = Listing.objects.get(pk=listing_id)
            user = request.user
            if listing.current_bid is None or placed_bid > listing.current_bid:
                new_bid = Bid(user=user, bid_amount=placed_bid, listing=listing)
                new_bid.save()
                listing.current_bid = placed_bid
                listing.save()
                return redirect(f'{reverse("listing", args=[listing_id])}?m=SnmbuiMJPIKlrSq68NTstBWfLCHhMmiPq6lgKoqFM')
            else:
                return redirect(f'{reverse("listing", args=[listing_id])}?m=pSQ3OwNeEpZX8iiXvuBKzkjt0k1D3Cfp3jyU8mUiL')
            
    return HttpResponseRedirect(reverse("listing",args={listing_id:listing_id}))

@login_required(login_url="login")
def watch_list(request):
    user_watchlist = Watchlist.objects.filter(user=request.user)
    listings = [item.listing for item in user_watchlist]
    return render(request, "auctions/watchlist.html",{
        "listings": listings,
    })

@login_required(login_url="login")
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user, listing=listing)
    if created:
        message = "Listing added to watchlist"
    else:
        message = "Listing is already in the watchlist"
    return redirect(f'{reverse("listing", args=[listing_id])}?a={message}')

@login_required(login_url="login")
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    watchlist = Watchlist.objects.filter(user=request.user, listing=listing)
    if watchlist.exists():
        watchlist.delete()
        message = "Listing removed from watchlist"
    else:
        message = "listing was not in your watchlist"
    return redirect(f'{reverse("index")}?a={message}')


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })
def category_listings(request, category_id):
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(category=category, active=True)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })
