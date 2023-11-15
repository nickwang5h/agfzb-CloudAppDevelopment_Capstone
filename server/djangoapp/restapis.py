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
def get_request(url, **kwargs):
    try:
        apikey = kwargs.get("apikey")
        params = {
            "text": kwargs.get("text"),
            "version": kwargs.get("version"),
            "features": kwargs.get("features"),
            "return_analyzed_text": kwargs.get("return_analyzed_text"),
        }

        headers = {"Content-Type": "application/json"}

        if apikey:
            response = requests.get(
                url,
                params=params,
                auth=HTTPBasicAuth("apikey", apikey),
                headers=headers,
            )
        else:
            response = requests.get(url, params=kwargs, headers=headers)

        response.raise_for_status()
        json_data = response.json()
        return json_data
    except Exception as e:
        print(f"Error in get_request: {e}")


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


def get_dealer_reviews_from_cf(url, **kwargs):
    review_id = kwargs.get("id")
    json_result = get_request(url, id=review_id) if review_id else get_request(url)
    results = [
        DealerReview(
            dealership=review.get("dealership"),
            id=review.get("id"),
            name=review.get("name"),
            review=review.get("review"),
            purchase=review.get("purchase"),
            purchase_date=review.get("purchase_date"),
            car_make=review.get("car_make"),
            car_model=review.get("car_model"),
            car_year=review.get("car_year"),
            sentiment=analyze_review_sentiments(review.get("review")),
        )
        for review in json_result
    ]
    return results
