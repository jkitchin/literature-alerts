import requests
import urllib.parse
from math import ceil
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup


def html_to_text(html_string):
    if html_string:
        soup = BeautifulSoup(html_string, 'html.parser')
        return soup.get_text()
    else:
        return html_string


def run_query(topic, since):
    # This does nothing if there is no .env. It is useful locally, but doesn't do
    # anything in the GitHUB action.
    load_dotenv() 
    API_KEY = os.environ['OPENALEX_API_KEY']

    API = 'https://api.openalex.org/works'

    results = []
    for _filter in topic['filter']:
        _filter += f',from_created_date:{since}'

        next_cursor = '*'
        while next_cursor:
            resp = requests.get(API, params={'api_key': API_KEY,
                                             'cursor': next_cursor,
                                             'filter': _filter})
            if resp.status_code == 200:
                data = resp.json()
            else:
                print(resp.text)
                raise Exception
            
            next_cursor = data['meta']['next_cursor']
            results += data['results']

    d = {}
    for result in results:
        d[result['id']] = result
    results = list(d.values())
    
    print('oa: ', len(results))
    return results


def get_abstract(result):
    """Return a rendered abstract for RESULT.
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

    return html_to_text(abstract)


def get_org_authors(result):
    """Return an author string for org-mode.
    Each author is linked to their id.
    """
    authors = [f"[[{au['author']['id']}][{au['author']['display_name']}]]"
               for au in result['authorships']]
    return ', '.join(authors)


def get_md_authors(result):
    """Return an author string for org-mode.
    Each author is linked to their id.
    """
    authors = [f"[{au['author']['display_name']}]({au['author']['id']})"
               for au in result['authorships']]
    return ', '.join(authors)


def get_authors(result):
    """Return a simple author string.
    """
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


def get_md_citation(result):
    """Return a lightly formatted citation for RESULT.
    """
    authors = get_md_authors(result)
    host = get_host(result)
    citation = f"{authors}, {host}. {result.get('biblio', {}).get('volume', 0)}({result.get('biblio', {}).get('issue', 0)})] {result['publication_year']}."
    return html_to_text(citation)


def get_org_citation(result):
    """Return a lightly formatted citation for RESULT.
    """
    authors = get_org_authors(result)
    host = get_host(result)
    citation = f"{authors}, {host}. {result.get('biblio', {}).get('volume', 0)}({result.get('biblio', {}).get('issue', 0)})] {result['publication_year']}."
    return html_to_text(citation)


def get_citation(result):
    """Return a lightly formatted citation for RESULT.
    """
    authors = get_authors(result)
    host = get_host(result)
    citation = f"{authors}, {host}. {result.get('biblio', {}).get('volume', 0)}({result.get('biblio', {}).get('issue', 0)})] {result['publication_year']}."
    return html_to_text(citation)
