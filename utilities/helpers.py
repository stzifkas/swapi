import requests
from utilities import config
from requests.models import HTTPError

base_url = config.base_url
def search_person(**kwargs):
    persons = []
    x = requests.get(
        "/".join([base_url, f"people/?name={kwargs['search_query']}"]))
    if not x.json()['result']:
        raise HTTPError
    results = x.json()['result']
    return results