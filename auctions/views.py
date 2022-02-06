from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import folium
import geocoder
from .models import *
from .forms import *

def index(request):
    m = folium.Map([40,-70],zoom_start= 5)
    
    listings = Listing.objects.all()
    for item in listings:
        location = geocoder.osm(item.address)
        lat = location.lat
        lng = location.lng
        try:
            folium.Marker([lat,lng], tooltip = item.item).add_to(m)
        except ValueError:
            folium.Marker([1,1],).add_to(m)
        
    m = m._repr_html_()
    return render(request, "auctions/index.html", {
        "listings":listings,
        "m" : m
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
        location = request.POST["location"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username = username, email = email, password = password, location = location)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = user
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })

@login_required
def show_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        if request.POST.get("button") == "watchlist": 
            if not user.watchlist.filter(listing= listing):
                watchlist = watchlist()
                watchlist.user = user
                watchlist.listing = listing
                watchlist.save()
            else:
                user.watchlist.filter(listing=listing).delete()
            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
        if not listing.closed:
            if request.POST.get("button") == "Close": 
                listing.closed = True
                listing.save()
            else:
                price = float(request.POST["price"])
                bids = listing.bids.all()
                if user.username != listing.owner.username: # only let those who dont own the listing be able to bid
                    if price <= listing.price:
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "form": BidForm(),
                            "message": "Error! Invalid bid amount!"
                        })
                    form = BidForm(request.POST)
                    if form.is_valid():
                        # clean up this
                        bid = form.save(commit=False)
                        bid.user = user
                        bid.save()
                        listing.bids.add(bid)
                        listing.price = price
                        listing.save()
                    else:
                        return render(request, 'auctions/listing.html', {
                            "form": form
                        })
        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "form": BidForm(),
            "message": ""
        })


@login_required
def watchlist(request):
    user = User.objects.get(username=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watchlist.all(),
        "dataset" : Data.objects.filter(user = User.objects.get(username=request.user)),
    })

def comment(request, listing_id):
    user = User.objects.get(username=request.user)
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = user
            comment.save()
            listing.comments.add(comment)
            listing.save()

            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
        else:
            return render(request, "auctions/comment.html", {
                "form": form,
                "listing_id": listing.id,
            })
    else:
        return render(request, "auctions/comment.html", {
            "form": CommentForm(),
            "listing_id": listing.id
        })

@login_required
def categories(request):
    return render(request, 'auctions/categories.html', {
        "categories": CATEGORIES,
    })

@login_required
def show_category_listings(request, category):
    listings = Listing.objects.filter(category= category)
    #cat = dict(CATEGORIES)
    return render(request, 'auctions/specific.html', {
        "listings": listings,
       # "category": cat[category]
    })

def createGraph(dataset):
    import numpy as np
    from sklearn.linear_model import LinearRegression
    data = []
    
    for i in range(len(dataset)):
        data.append([i,dataset[i].inventory - dataset[i].leftover])
    X = np.array(data)[:,0].reshape(-1,1)
    y = np.array(data)[:,1].reshape(-1,1)
    to_predict_x= [len(data) +1 ,len(data) + 2, len(data) + 3, len(data) + 4, len(data) + 5, len(data) + 6, len(data) + 7]
    to_predict_x= np.array(to_predict_x).reshape(-1,1)

    regsr=LinearRegression()
    regsr.fit(X,y)
    predicted_y= regsr.predict(to_predict_x)
    m= regsr.coef_
    c= regsr.intercept_
    import matplotlib.pyplot as plt

    plt.title('Predict the amount of inventory needed')  
    plt.xlabel('Days')  
    plt.ylabel('Amount') 
    plt.scatter(X,y,color="blue")
    new_y=[ m*i+c for i in np.append(X,to_predict_x)]
    new_y=np.array(new_y).reshape(-1,1)
    plt.plot(np.append(X,to_predict_x),new_y,color="red")

    plt.savefig('graph.png')

    return predicted_y , "graph.png"


def graph(request):
    date = request.POST["date"]
    inventory = request.POST["inventory"]
    leftover = request.POST["leftover"]

    newData = Data.objects.create(date = date, inventory = inventory, leftover = leftover, sold = int(inventory) - int(leftover), user = User.objects.get(username=request.user) )
    newData.save()
    
    dataset = Data.objects.filter(user = User.objects.get(username=request.user))
    predicted, pic = createGraph(dataset)
    return render(request, 'auctions/watchlist.html', {
        "dataset" : dataset,
        "item1" : round(predicted[0][0]),
        "item2" : round(predicted[1][0]),
        "item3" : round(predicted[2][0]),
        "item4" : round(predicted[3][0]),
        "item5" : round(predicted[4][0]),
        "item6" : round(predicted[5][0]),
        "item7" : round(predicted[6][0]),
    })

