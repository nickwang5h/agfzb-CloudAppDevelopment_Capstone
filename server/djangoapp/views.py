from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

# from .models import related models
from .models import CarModel, CarMake, CarDealer, DealerReview

# from .restapis import related methods
from .restapis import (
    get_request,
    post_request,
    get_dealers_from_cf,
    get_dealer_reviews_from_cf,
    get_dealer_by_id_from_cf,
)
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/about.html", context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/contact.html", context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context["message"] = "Invalid username and password."
            return render(request, "djangoapp/index.html", context)
    else:
        return render(request, "djangoapp/index.html", context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect("djangoapp:index")


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    """
    Handle registration requests.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    context = {}

    if request.method == "GET":
        return render(request, "djangoapp/registration.html", context)

    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        user_exist = False

        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))

        if not user_exist:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            login(request, user)
            return redirect("djangoapp:index")

        else:
            context["message"] = "User already exists."
            return render(request, "djangoapp/registration.html", context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
# def get_dealerships(request):
#     context = {}
#     if request.method == "GET":
#         return render(request, "djangoapp/index.html", context)


def get_dealerships(request):
    """
    This function retrieves a list of dealerships from a remote server
    and renders the result in a Django template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.
    """
    if request.method == "GET":
        url = "https://congwang5h-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context = {"dealerships": dealerships}
        return render(request, "djangoapp/index.html", context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    """
    Retrieves the details of a dealer and their reviews.

    Args:
        request: The HTTP request object.
        dealer_id: The ID of the dealer.

    Returns:
        The rendered HTML template with the dealer details and reviews.
    """
    dealer_url = "https://congwang5h-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
    review_url = "https://congwang5h-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"

    dealer = get_dealer_by_id_from_cf(dealer_url, id=dealer_id)
    reviews = get_dealer_reviews_from_cf(review_url, dealer_id=dealer_id)

    context = {"dealer": dealer, "reviews": reviews}

    return render(request, "djangoapp/dealer_details.html", context)


# Create a `add_review` view to submit a review


def add_review(request, id):
    """
    Add a review for a specific dealership.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the dealership.

    Returns:
        HttpResponseRedirect: A redirect to the dealer details page.

    Raises:
        ValueError: If the car ID is invalid.
    """

    # Initialize the context dictionary
    context = {}

    # Get the dealer information
    dealer_url = "https://congwang5h-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
    context["dealer"] = dealer

    # Handle GET request
    if request.method == "GET":
        # Get all car models
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, "djangoapp/add_review.html", context)

    # Handle POST request
    elif request.method == "POST":
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Get the username
            username = request.user.username

            # Create the payload for the review
            payload = {}
            car_id = request.POST["car"]
            try:
                car = CarModel.objects.get(pk=car_id)
            except CarModel.DoesNotExist:
                raise ValueError("Invalid car ID")

            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = id
            payload["id"] = id
            payload["review"] = request.POST["content"]
            payload["purchase"] = request.POST.get("purchasecheck") == "on"
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.make.name
            payload["car_model"] = car.name
            payload["car_year"] = int(car.year.strftime("%Y"))

            new_payload = {"review": payload}
            review_post_url = "https://congwang5h-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"

            # Send the review payload to the API
            post_request(review_post_url, new_payload, id=id)

        # Redirect to the dealer details page
        return redirect("djangoapp:dealer_details", id=id)
