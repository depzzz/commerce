from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib import messages
from .models import User, listings, watchlist, bids, winner, comments

# Categories for Listing Creation
CATEGORIES = [
    ("ENTERTAINMENT", "Entertainment"),
    ("ELECTRONICS", "Electronics"),
    ("FASHION", "Fashion"),
    ("GENERAL", "General"),
    ("HOME", "Home"),
    ("TOYS", "Toys"),
]

# form for creating of a new listing
class CreateForm(forms.Form):
    title = forms.CharField(label='Enter Title',max_length=64)
    description = forms.CharField(label='Enter Listing Description',max_length=250)
    starting_price = forms.IntegerField(label='Enter Bid Starting Price',min_value=1)
    image_url = forms.URLField(label='Enter Image Url',max_length=200)
    category = forms.ChoiceField(
        label='Choose a Category',
        choices= CATEGORIES,
        widget= forms.RadioSelect
    )

# form for bidding
class BidForm(forms.Form):
    bid_amount = forms.IntegerField(label="Enter Bid Amount",
                                required=True)
    
# form for adding a comment
class CommentForm(forms.Form):
    comment = forms.CharField(label='Comment',
                            widget=forms.Textarea,
                            required=True)
    

# default route index for showing all the active listings
def index(request):
    # Get active listings from the listings table
    context = {"listings": listings.objects.filter(status='O')}
    return render(request, "auctions/index.html",context)

# login page route
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

# logout route, for logging the user out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# register route, for creation of a new user
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

# create route, renders a form for new listing creation and saves it into db
@login_required(login_url='login')
def create_listing(request):
    if request.method == "POST":
        # Create a Listing & Add the same to database
        form = CreateForm(request.POST)

        # Get Data From Form & Check whether it is valid 
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            starting_price = form.cleaned_data['starting_price']
            image_url = form.cleaned_data['image_url']
            category = form.cleaned_data['category']

            # insert the data into listings table
            new_listing = listings(title=title,
                                description=description,
                                current_price=starting_price,
                                image_url=image_url,
                                category=category,
                                owner=User.objects.get(pk=request.user.id))
            new_listing.save()

            # go back to the listing page and 
            # show an alert that the listing was added successfully
            return redirect('index')
        else:
            # show validation errors of forms
            messages.warning(request, 'There were errors in your form, please recheck and submit again!')
            return redirect('create')
    else:
    # if the request is get then render create listing form
        context = {"CreateForm" : CreateForm}
        return render(request, "auctions/create.html", context)

# view listing route, shows all the details of a particular listing and lets the user do things
def view_listing(request,id):
    # define current listing
    current_listing = listings.objects.get(pk=id)

    if request.user.is_authenticated:
        # define current user
        current_user = User.objects.get(pk=request.user.id)

        # get listing comments
        all_comments = comments.objects.filter(listingid=current_listing)

        # check if the current listing is closed
        if current_listing.status == 'C':
            # get the current listing winner
            listing_winner = User.objects.get(pk=winner.objects.get(listingid=current_listing).winner.id)
        else:
            listing_winner = ''

        # check if the current user is the listing winner
        if current_user == listing_winner:
            message_for_winner = "Congratulations! You are the winner of this bid."
        else:
            message_for_winner = ''

        # dealing with bids that the user makes
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['bid_amount']
            # if the bid amount is greater than the current amount then add the bid 
            # and update the current amount
            if bid_amount > current_listing.current_price:
                new_bid = bids(user=current_user,
                            listingid=current_listing,
                            bid_amount=bid_amount)
                new_bid.save()

                current_listing.current_price = bid_amount
                current_listing.save()
            # if the bid amount is smaller than the current amount then redirect the user
            # to the listing page and show them an error
            else:
                messages.warning(request, 'Bid amount must be greater than current bid price!')
                redirect('view',id)
        
        # check if the current user is the one who made the bid
        if current_listing.status == 'C':
            close_bid = ''
        elif current_user == current_listing.owner:
            close_bid = "Close the Bid"
        else:
            close_bid = ''

        # check if the listing already exists in current user's watchlist
        already_exists = watchlist.objects.filter(user=current_user,listingid=current_listing)

        # if not, then show "Add to Watchlist" Option
        if not already_exists:
            add_or_remove = "Add To Watchlist"
            context = {
                "listing": listings.objects.get(pk=id),
                "add_or_remove" : add_or_remove,
                "BidForm" : BidForm,
                "close_bid" : close_bid,
                "message_for_winner" : message_for_winner,
                "CommentForm" : CommentForm,
                "all_comments" : all_comments
            }
            return render(request, "auctions/listing.html",context)

        # if so, then show "Remove From Watchlist" Option
        else:
            add_or_remove = "Remove From Watchlist"
            context = {
                "listing": listings.objects.get(pk=id),
                "add_or_remove" : add_or_remove,
                "BidForm" : BidForm,
                "close_bid" : close_bid,
                "message_for_winner" : message_for_winner,
                "CommentForm" : CommentForm,
                "all_comments" : all_comments
            }
            return render(request, "auctions/listing.html",context)
    else:
        # if user is not authenticated, show them a message asking them to login
        message = "Create an Accuont to Start Bidding"

        # get listing comments
        all_comments = comments.objects.filter(listingid=current_listing)

        context = {
                "listing": listings.objects.get(pk=id),
                "message" : message,
                "all_comments" : all_comments
            }
        return render(request, "auctions/listing.html",context)
        

# lets the user add a listing to their watchlist
@login_required(login_url='login')
def add_watchlist(request,id):
    # define current user
    current_user = User.objects.get(pk=request.user.id)

    # define current listing
    current_listing = listings.objects.get(pk=id)

    # check if the listing already exists in current user's watchlist
    already_exists = watchlist.objects.filter(user=current_user,listingid=current_listing)

    # if not, then add the listing to user's watchlist
    if not already_exists:
        add = watchlist(
            user=current_user,
            listingid=current_listing
        )
        add.save()
        return redirect('view',id)
    
    # if so, then delete the listing from user's watchlist
    else:
        already_exists.delete()
        return redirect('view',id)

@login_required(login_url='login')
def close_listing(request,id):
    # define current user
    current_user = User.objects.get(pk=request.user.id)

    # define current listing
    current_listing = listings.objects.get(pk=id)

    # check if the current user is the one who made the bid
    if current_user == current_listing.owner:
        current_listing.status = 'C'
        current_listing.save()
    
        # add the data of the winner to the winners table
        listing_winner = User.objects.get(pk=bids.objects.filter(listingid=current_listing.id).last().user.id)

        title = current_listing.title
        bid_amount = current_listing.current_price

        # insert the data into winners table
        new_winner = winner(winner=listing_winner,
                            owner=current_user,
                            listingid=current_listing,
                            title=title,
                            bid_amount=bid_amount)
        new_winner.save()
        return redirect('view',id)

@login_required(login_url='login')
def add_comment(request,id):
    # define current user
    current_user = User.objects.get(pk=request.user.id)

    # define current listing
    current_listing = listings.objects.get(pk=id)

    if request.method == "POST":
        # Add a Comment to the Current Listing Page
        form = CommentForm(request.POST)

        # Get Data From CommentForm Present in listing.html & Check whether it is valid 
        if form.is_valid():
            add_comment = form.cleaned_data['comment']

            # insert the data into comments table
            new_comment = comments(user=current_user,
                                listingid=current_listing,
                                comment=add_comment)
            new_comment.save()

            return redirect('view',id)
        else:
            # show validation errors of forms
            messages.warning(request, 'The Comment Field Cannot be Empty')
            return redirect('view',id)
            
# shows the user their watchlist
@login_required(login_url='login')
def view_watchlist(request):
    # define current user
    current_user = User.objects.get(pk=request.user.id)

    # retrive user added listings from watchlist 
    # objects.filter always returns a queryset
    listing_ids = watchlist.objects.filter(user=current_user).values('listingid')
    
    # get listind data from queryset 
    items = listings.objects.filter(id__in=listing_ids)

    # render template
    context = {
        "items" : items
    }

    return render(request, 'auctions/watchlist.html', context)