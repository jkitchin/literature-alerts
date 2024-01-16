import requests
import urllib.parse
from math import ceil
from dotenv import load_dotenv
import os


def run_query(topic, since):
    # This does nothing if there is no .env. It is useful locally, but doesn't do
    # anything in the GitHUB action.
    load_dotenv() 
    API_KEY = os.environ['OPENALEX_API_KEY']

    API = 'https://api.openalex.org/works?filter='

    results = []
    for _filter in topic['filter']:
        url = (API + urllib.parse.quote(_filter)
               + f',from_created_date:{since}')
        print(url)
        url += f'&api_key={API_KEY}'

        data = requests.get(url).json()

        count = data['meta']['count']
        perpage = data['meta']['per_page']
        npages = ceil(count / perpage)

        results += data['results']

        
        for i in range(1, npages):
            purl = url + f'&page={i}'
            data = requests.get(url).json()
            results += data['results']

                
    print('oa: ', results)
    return results
