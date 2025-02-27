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


def post_request(url, json_payload, **kwargs):
    response = requests.post(url, params=kwargs, json=json_payload)
    return response


def get_dealers_from_cf(url):
    """
    Fetch dealers from a cloud function.

    Args:
    - url (str): The URL to fetch dealers from.

    Returns:
    - list[CarDealer]: A list of CarDealer objects.
    """
    try:
        json_result = get_request(url)
        if json_result:
            dealers = []
            for dealer in json_result:
                # Create a CarDealer instance with the modified dealer dictionary
                dealers.append(CarDealer(**dealer))
            return dealers
        else:
            return []
    except Exception as e:
        print(f"Error fetching dealers: {e}")
        return []


def get_dealer_by_id_from_cf(url, id):
    """
    Get a dealer by ID from a cloud function.

    Args:
    - url (str): The URL to fetch the dealer from.
    - id (int): The ID of the dealer.

    Returns:
    - CarDealer: A CarDealer object.
    """
    try:
        dealer_data = get_request(url, params={"id": id})
        if dealer_data:
            return CarDealer(**dealer_data[0])
        else:
            return None
    except Exception as e:
        print(f"Error fetching dealer by ID: {e}")
        return None


def analyze_review_sentiments(dealer_review):
    url = "https://sn-watson-sentiment-bert.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/SentimentPredict"
    myobj = {"raw_document": {"text": dealer_review}}
    header = {
        "grpc-metadata-mm-model-id": "sentiment_aggregated-bert-workflow_lang_multi_stock"
    }
    response = requests.post(url, json=myobj, headers=header)
    formatted_response = json.loads(response.text)
    if response.status_code == 200:
        label = formatted_response["documentSentiment"]["label"]
        score = formatted_response["documentSentiment"]["score"]
        print(label, score)
    elif response.status_code == 500:
        label = None
        score = None
    return label


def get_dealer_reviews_from_cf(url, id):
    try:
        reviews_data = get_request(url, params={"id": id})
        if reviews_data:
            dealer_reviews = []
            for review in reviews_data:
                review_obj = DealerReview(**review)
                # Analyze the sentiment of the review
                sentiment = analyze_review_sentiments(review_obj.review)
                print(sentiment)  # Print the sentiment
                review_obj.sentiment = (
                    sentiment  # Assign sentiment to the review object
                )
                dealer_reviews.append(review_obj)
            return dealer_reviews
        else:
            return []
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return []
