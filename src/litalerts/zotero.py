"""Proof of concept for integration with Zotero.

"""

from pyzotero import zotero
from dotenv import load_dotenv
import click
import datetime
from yaml import load, Loader
import os
import requests
from nameparser import HumanName
from .openalex import get_abstract, run_query

load_dotenv()


def write_zotero_results(zot, results, today, tags=()):
    """Write results to a Zotero library.
    zot : an instance of zotero.Zotero
    """
    # check if we have this already. I don't love this approach, I get all
    # the items in the library first.
    N = zot.count_items()
        
    limit = 50
    pages = (N // limit) + 1
        
    items = []
    for i in range(pages):
        items += zot.items(limit=limit, start=i * limit)

    # Store known urls
    urls = {item['data'].get('url', None): True for item in items}

    for result in results:
        if not result['type_crossref'] == 'journal-article':
            print(f'skipping {result["id"]}, {result["type_crossref"]}')

        if result['id'] in urls:
            print(f'we already got {result["id"]}.')
            continue

        t = zot.item_template('journalArticle')

        t['title'] = result['title']
        t['DOI'] = result['doi']
        t['url'] = result['id']
        pl = result['primary_location']
        if pl:
            source = pl['source']
        else:
            source = None
        if source:
            dn = source['display_name']
        else:
            dn = None
        t['publicationTitle'] = dn

        at = t['creators'][0]
        t['creators'] = []
        for i, author in enumerate(result['authorships']):
            t['creators'] += [at.copy()]
            hn = HumanName(author['author']['display_name'])
            # I am not sure this is the best thing to do for the first/last name.
            t['creators'][i]['firstName'] = ' '.join([hn.first, hn.middle])
            t['creators'][i]['lastName'] = hn.last

        t['volume'] = result['biblio']['volume']
        t['issue'] = result['biblio']['issue']
        t['pages'] = f"{result['biblio']['first_page']}-{result['biblio']['last_page']}"
        t['date'] = result['publication_date']
        t['abstractNote'] = get_abstract(result)
        t['dateAdded'] = today.strftime("%Y-%m-%d %H:%M:%S")
        if tags:            
            t['tags'] = [{'tag': tag} for tag in tags]

        resp = zot.create_items([t])
        if len(resp['success']) != 1:
            print(resp)

            
@click.command()
@click.argument('query')
@click.option('-z', '--zotero-id', default='',
              help='Zotero id for library to add to. It should be user/<userid> or groups/<groupid>')
def oa_zotero(query, zotero_id):
    """query is a filter, e.g. author.id:a5003442464

    example command: oa-zotero -z user/37559 author.id:a5003442464

    """
    API_KEY = os.environ['OPENALEX_API_KEY']

    # Get the OpenAlex results
    API = 'https://api.openalex.org/works'
    results = []
    next_cursor = '*'
    while next_cursor:
        data = requests.get(API, params={'api_key': API_KEY,
                                         'cursor': next_cursor,
                                         'filter': query}).json()
        next_cursor = data['meta']['next_cursor']
        results += data['results']

    d = {}
    for result in results:
        d[result['id']] = result
    results = list(d.values())

        
    ZOTERO_API_KEY = os.environ['ZOTERO_API_KEY']
    ztype, zotero_id = zotero_id.split('/')
    zot = zotero.Zotero(zotero_id, ztype, ZOTERO_API_KEY)

    today = datetime.date.today()
    write_zotero_results(zot, results, today)
    
    

@click.command()
@click.option('-f', '--fname', default='queries.yml', help='yml file with queries')              
@click.option('-s', '--since', default=7, help='days since')
def update_zotero(fname, since):
    """Load FNAME and get results from SINCE.
    FNAME is a yaml file with a set of queries in it. It should also contain a zotero_id.
    SINCE is the number of days since new items were added.

    You need a ZOTERO_API_KEY in your environment.

    This currently only updates journal articles.
    """
    
    today = datetime.date.today()
    _since = (today - datetime.timedelta(days=since)).strftime("%Y-%m-%d")

    with open(fname, 'r') as f:
        queries = load(f.read(), Loader=Loader)

    for topic in queries['queries']:
        if 'zotero_id'not in topic:
            raise Exception(f'No zotero_id found in {topic}')

        topic['today'] = today
        topic['since'] = _since
        results = run_query(topic, _since)

        ZOTERO_API_KEY = os.environ['ZOTERO_API_KEY']
        zytype, zotero_id = topic['zotero_id'].split('/')
        zot = zotero.Zotero(zotero_id, zytype, ZOTERO_API_KEY)

        tags = ['unread']
        if 'tag' in topic:
            tags += [topic['tag']]
        write_zotero_results(zot, results, today, tags)





