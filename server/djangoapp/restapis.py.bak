import requests
import json
import os

# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, DealerReview
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import (
    Features,
    EntitiesOptions,
    KeywordsOptions,
    EmotionOptions,
    SentimentOptions,
)


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, params=None, apikey=None):
    """
    Make an HTTP GET request to a specified URL.

    Args:
    - url (str): The URL to make the GET request to.
    - params (dict, optional): Parameters to be sent with the request.
    - apikey (str, optional): API key for authentication, if needed.

    Returns:
    - dict: JSON response from the request.
    """
    try:
        # Set headers and authentication
        headers = {"Content-Type": "application/json"}
        auth = HTTPBasicAuth("apikey", apikey) if apikey else None

        # Make the GET request
        response = requests.get(url, params=params, headers=headers, auth=auth)

        # Check if the response was successful
        response.raise_for_status()

        # Return the JSON data from the response
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error during request: {req_err}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    response = requests.post(url, params=kwargs, json=json_payload)
    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    res = get_request(url)

    if res:
        dealers = res

        for dealer in dealers:
            dealer_obj = CarDealer(
                address=dealer["address"],
                city=dealer["city"],
                full_name=dealer["full_name"],
                id=dealer["id"],
                lat=dealer["lat"],
                long=dealer["long"],
                short_name=dealer["short_name"],
                state=dealer["state"],
                st=dealer["st"],
                zip=dealer["zip"],
            )
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, id, **kwargs):
    res = get_request(url, id=id)
    if res:
        dealer = res[0]
        dealer_obj = CarDealer(
            address=dealer["address"],
            city=dealer["city"],
            full_name=dealer["full_name"],
            id=dealer["id"],
            lat=dealer["lat"],
            long=dealer["long"],
            short_name=dealer["short_name"],
            state=dealer["state"],
            st=dealer["st"],
            zip=dealer["zip"],
        )

    return dealer_obj


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealer_review):
    apikey = os.environ.get("IBM_API_KEY")
    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version="2022-04-07", authenticator=authenticator
    )
    natural_language_understanding.set_service_url("")

    features = Features(sentiment=SentimentOptions(targets=[dealer_review]))
    response = natural_language_understanding.analyze(
        text=dealer_review, language="en", features=features
    ).get_result()

    return response["sentiment"]["document"]["label"]


def get_dealer_reviews_from_cf(url, dealer_id):
    """
    Get dealer reviews from a cloud function.

    Args:
    - url (str): The URL to make the GET request to.
    - dealer_id (int): The ID of the dealer for which to get reviews.

    Returns:
    - list: A list of DealerReview objects.
    """
    try:
        # Define the parameters for the request
        params = {"dealerId": dealer_id}

        # Call the get_request function
        json_result = get_request(url, params)

        # Process the JSON result into DealerReview objects
        reviews = []
        for review in json_result:
            sentiment = analyze_review_sentiments(review.get("review"))
            dealer_review = DealerReview(
                dealership=review.get("dealership"),
                id=review.get("id"),
                name=review.get("name"),
                review=review.get("review"),
                purchase=review.get("purchase"),
                purchase_date=review.get("purchase_date"),
                car_make=review.get("car_make"),
                car_model=review.get("car_model"),
                car_year=review.get("car_year"),
                sentiment=sentiment,
            )
            reviews.append(dealer_review)

        return reviews

    except Exception as e:
        print(f"Error in get_dealer_reviews_from_cf: {e}")
        return []
