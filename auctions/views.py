from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Max


from .models import User, AuctionCategories, AuctionListings, Bids, Comments, Watchlist


def index(request):
    bids = Bids.objects.all()
    actives = AuctionListings.objects.filter(active=True)
    # Add greater bid with actives
    for active in actives:
        for bid in bids:
            if active == bid.listing:
                if hasattr(active, 'current_price'):
                    if (active.current_price < bid.current_price):
                        active.current_price = bid.current_price
                else:
                    active.current_price = bid.current_price
    return render(request, "auctions/index.html", {
        "actives": actives,
        "bids": bids
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


@login_required(login_url='/login')
def create(request):
    categories = AuctionCategories.objects.all()
    if request.method == "POST":
        title = (request.POST["title"])
        description = (request.POST["description"])
        imageUrl = (request.POST["imageUrl"])
        try:
            category = AuctionCategories.objects.get(pk=int(request.POST["category"]))
        except AuctionCategories.DoesNotExist:
            category = None
        starting_bid = (request.POST["starting_bid"])
        # To create new listing
        listing = AuctionListings(title=title, description=description, imageUrl=imageUrl,  starting_bid=starting_bid, user=request.user, category=category)
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    return render(request, "auctions/create.html", {
        "categories": categories
    })


def listing(request, listing_id):
    count_bid = 0
    greater_bid = None
    try:
        listing = AuctionListings.objects.get(pk=listing_id)
    except AuctionListings.DoesNotExist:
        return HttpResponseRedirect(reverse("index",))
    # Status Listing
    status = {"listing": None, "btn_class": None, "btn_text": None}
    if listing.active == True:
        status["listing"] = False
        status["btn_class"] = "btn-outline-danger"
        status["btn_text"] = "Close Auction"
    else:
        status["listing"] = True
        status["btn_class"] = "btn-outline-success"
        status["btn_text"] = "Open Auction"
    # Checking if there is any bid and select the bids, order by greater bid
    try:
        bids = Bids.objects.filter(listing=listing_id).annotate(Max('current_price')).order_by('-current_price__max')
        # Counting how many bids
        count_bid = len(bids)
    except Bids.DoesNotExist:
        bids = None
        greater_bid = None
    # Select the greater bid
    if count_bid > 0:
        greater_bid = bids[0]
    # Get the comments
    try:
        comments = Comments.objects.filter(listing=listing_id)
    except Comments.DoesNotExist:
        comments = None
    # Get status watchlist
    watchlist_status = None
    if request.user.is_authenticated:
        try:
            watcher = Watchlist.objects.get(user=request.user, listing=listing_id)
            watchlist_status = True
        except Watchlist.DoesNotExist:
            watchlist_status = False
    # Register the bid
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        bid_user = float(request.POST["bid_user"].replace(',', ''))
        listing_bid = AuctionListings.objects.get(pk=listing_id)
        bids = Bids.objects.filter(listing=listing_id).annotate(Max('current_price')).order_by('-current_price__max')
        if bid_user > listing_bid.starting_bid and bid_user > bids[0].current_price:
            bidsave = Bids(user=request.user, listing=listing_bid, current_price=bid_user)
            bidsave.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        else:
            return render(request, "auctions/listing.html", {
                "message": "ERROR: The bid must be greater than the current price.",
                "listing": listing,
                "greater_bid": greater_bid,
                "count_bid": count_bid,
                "comments": comments,
                "status": status,
                "watchlist_status": watchlist_status
            })
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "greater_bid": greater_bid,
        "count_bid": count_bid,
        "comments": comments,
        "status": status,
        "watchlist_status": watchlist_status
    })


@login_required(login_url='/login')
def comments(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        comment = request.POST["comment"]
        listing = AuctionListings.objects.get(pk=listing_id)
        comments = Comments(user=request.user, listing=listing, comment=comment)
        comments.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    return HttpResponseRedirect(reverse("index",))


@login_required(login_url='/login')
def active(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        active_listing = request.POST["active"]
        listing = AuctionListings.objects.get(pk=listing_id)
        listing.active = active_listing
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    return HttpResponseRedirect(reverse("index",))


@login_required(login_url='/login')
def watchlist(request):
    try:
        watchers = Watchlist.objects.filter(user=request.user)
    except Watchlist.DosNotExist:
        watchers = None
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        watchlist_value = request.POST["watchlist_value"]
        listing = AuctionListings.objects.get(pk=listing_id)
        if watchlist_value == "add":
            watcher = Watchlist(user=request.user, listing=listing)
            watcher.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        else:
            watcher = Watchlist.objects.get(user=request.user, listing=listing_id)
            watcher.delete()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    listings = []
    for watcher in watchers:
        listings.append(AuctionListings.objects.get(listing=watcher))
    # Add greater bid with actives
    bids = Bids.objects.all()
    for listing in listings:
        for bid in bids:
            if listing == bid.listing:
                if hasattr(listing, 'current_price'):
                    if (listing.current_price < bid.current_price):
                        listing.current_price = bid.current_price
                else:
                    listing.current_price = bid.current_price
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def categories(request):
    categories = AuctionCategories.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category_id):
    try:
        category = AuctionCategories.objects.get(pk=category_id)
    except AuctionCategories.DoesNot.Exist:
        return HttpResponseRedirect(reverse("categories"))
    try:
        listings = AuctionListings.objects.filter(category=category, active=True)
    except AuctionListings.DoesNotExist:
        listings = None
    # Add greater bid with actives
    bids = Bids.objects.all()
    for listing in listings:
        for bid in bids:
            if listing == bid.listing:
                if hasattr(listing, 'current_price'):
                    if (listing.current_price < bid.current_price):
                        listing.current_price = bid.current_price
                else:
                    listing.current_price = bid.current_price
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category
    })