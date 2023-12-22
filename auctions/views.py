from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import  HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import ListingForm
from django.contrib import messages
from .models import Bid, Category, Listing, User
from .forms import CommentForm



def index(request):
    active_listings = Listing.objects.filter(active=True)
    return render(request, 'auctions/index.html', {'active_listings': active_listings})


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


@login_required # We use a django funtion that ensures that the user is logged in before the user can access this view
def create_listing(request): #This is the function that creates the listing
    if request.method == 'POST': 
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            return redirect('index')  # Redirect to the index or listing page
    else:
        form = ListingForm()

    return render(request, 'auctions/create_listing.html', {'form': form})

def listing_view(request, listing_id): # This function is used to display the listing, where we fetch the listing and the comments
    listing = get_object_or_404(Listing, pk=listing_id) 
    comments = listing.comments.all()  #
    on_watchlist = False

    if request.user.is_authenticated:
        on_watchlist = listing.watchers.filter(pk=request.user.pk).exists() # Here we check if the user is on the watchlist

        # Handling watchlist toggle
        if 'watchlist_toggle' in request.POST:
            if on_watchlist:
                listing.watchers.remove(request.user)
            else:
                listing.watchers.add(request.user)
            return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
        
        # Handling comment submission
    if request.method == 'POST' and 'post_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        # Here we check if the comment is valid and save it and the listing and user as well. 
        if comment_form.is_valid(): 
            comment = comment_form.save(commit=False) 
            comment.listing = listing 
            comment.user = request.user 
            comment.save()
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    else:
        comment_form = CommentForm() # Creating a new comment form

    return render(request, 'auctions/listing_page.html', {
        'listing': listing,
        'comment_form': comment_form
    })

@login_required # look at line 72 for explanation. This applies to the other places we use this function
def watchlist(request): # This funtion is used to display the user's watchlist
    return render(request, 'auctions/watchlist_page.html', { 
        'watchlist': request.user.watched_listings.all() 
    })

@login_required
# This function is used to place a bid on a listing 
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id) # Fetching the listing
    if not listing.active: # Checking if the listing is active
        messages.error(request, "This auction is no longer active.")
        return redirect('listing', listing_id=listing.id)

    if request.method == "POST": 
        try:
            bid_amount = float(request.POST.get('bid_amount', 0)) # Fetching the bid amount
        except ValueError:
            messages.error(request, "Invalid bid amount.") # Handling invalid bid amount
            return redirect('listing', listing_id=listing.id) # Redirecting to the listing page

        # Find the current maximum bid for this listing
        current_max_bid = listing.bid_set.order_by('-amount').first()
        current_max_bid_amount = current_max_bid.amount if current_max_bid else listing.starting_bid

        # Check if the bid is valid
        if bid_amount <= current_max_bid_amount:
            messages.error(request, "Your bid must be higher than the current bid.")
        else:
            # If the bid is valid, process it
            Bid.objects.create(user=request.user, listing=listing, amount=bid_amount)
            # Here we update the current bid of the listing
            listing.current_bid = bid_amount
            listing.save()
            messages.success(request, "Your bid was placed successfully!")

        return redirect('listing', listing_id=listing.id)
    else:

        return redirect('listing', listing_id=listing.id)

@login_required
def close_auction(request, listing_id): # In this function we closed the auction and set the winner of the auction
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)

    if request.method == "POST":
        listing.active = False

        # We find here the highest bid for this listing
        highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

        if highest_bid:
            # Set the winner of the auction
            listing.winner = highest_bid.user
            messages.success(request, f"The auction has been closed successfully. The winner is {listing.winner.username}.") # Here we print out a message to the user if the auction has been closed successfully
        else:
            messages.info(request, "The auction has been closed. There were no bids on this listing.") # Here we print out a message to the user if the auction has been closed successfully but there were no bids on the listing

        listing.save()
        return redirect('listing', listing_id=listing.id)
    
    return redirect('listing', listing_id=listing.id)

@login_required
def watchlist_view(request): # This function is used to display the user's watchlist
    user_watchlist = request.user.watchlist.all()
    return render(request, 'auctions/watchlist_page.html', {'watchlist': user_watchlist})

def category_list(request): # This function is used to display the categories for the user's watchlist
    categories = Category.objects.all()
    return render(request, 'auctions/category_list_page.html', {'categories': categories})

def listings_by_category(request, category_id): # Here we display the listings by category
    category = get_object_or_404(Category, pk=category_id)
    listings = Listing.objects.filter(category=category, active=True)
    return render(request, 'auctions/listings_by_category.html', {'category': category, 'listings': listings})