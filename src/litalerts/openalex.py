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

    results = list(set(results))   
    print('oa: ', len(results))
    return results


def get_abstract(result):
    """Retrun a rendered abstract for RESULT.
    """
    aii = result.get('abstract_inverted_index', None)
    word_index = []
    
    if aii:
        for k,v in aii.items():
            for index in v:
                word_index.append([k, index])

        word_index = sorted(word_index,key = lambda x : x[1])
        abstract = ' '.join([x[0] for x in word_index])
    else:
        abstract = 'No abstract'

    return abstract


def get_authors(result):
    return ', '.join([au['author']['display_name'] for au in result['authorships'] ])


def get_host(result):
    """Get the host for RESULT.
    This is usually a journal name.
    """
    source = result.get('primary_location', {}).get('source', {})
    if source:
        host = source.get('display_name', 'No host')
    else:
        host = 'No host'
    return host


def get_citation(result):
    """Return a lightly formatted citation for RESULT.
    """
    authors = get_authors(result)
    host = get_host(result)
    return f"{authors}, {host}. {result.get('biblio', {}).get('volume', 0)}({result.get('biblio', {}).get('issue', 0)})] {result['publication_year']}." 
