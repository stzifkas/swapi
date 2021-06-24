"""Handles requests to Star Wars API
"""
import requests
from requests.models import HTTPError
from utilities import config

def search_person(**kwargs):
    """Performs a person search using SWAPI people endpoint

    Raises:
        HTTPError: If no result is returned

    Returns:
        [dict]: list of dictionaries with persons' properties
    """
    response = requests.get(
        "/".join([config.BASE_URL, f"people/?name={kwargs['search_query']}"]))
    if not response.json()['result']:
        raise HTTPError
    results = response.json()['result']
    return results


def homeworld_from_url(**kwargs):
    """Retrieves homeworld from a given SWAPI endpoind

    Raises:
        HTTPError: If no result is returned

    Returns:
        dict: A dictionary with world's properties
    """
    response = requests.get(kwargs['url'])
    if not response.json()['result']:
        raise HTTPError
    result = response.json()['result']
    return result
