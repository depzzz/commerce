from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from .models import User, listings

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
                                starting_price=starting_price,
                                image_url=image_url,
                                category=category,
                                owner=request.user.username)
            new_listing.save()

            # go back to the listing page and 
            # show an alert that the listing was added successfully
            return HttpResponse("Added Successfully!")
        else:
            # show validation errors of forms
            return HttpResponse("Something Wrong Happened!")
    else:
    # if the request is get then render create listing form
        context = {"CreateForm" : CreateForm}
        return render(request, "auctions/create.html", context)