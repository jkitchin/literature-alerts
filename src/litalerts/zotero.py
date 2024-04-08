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
        zotero_id = topic['zotero_id']
        results = run_query(topic, _since)

        ZOTERO_API_KEY = os.environ['ZOTERO_API_KEY']
        zot = zotero.Zotero(zotero_id, 'group', ZOTERO_API_KEY)

        for result in results:
            if not result['type_crossref'] == 'journal-article':
                print(f'skipping {result["id"]}, {result["type_crossref"]}')

            title = result['title']

            # check if we have this already
            if len(zot.items(q=title)) > 0:
                print(f'we already got {title}.')
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
            t['tags'] = [{'tag': 'unread'}]
            if 'tag' in topic:
                t['tags'] += [{'tag': topic['tag']}]
            resp = zot.create_items([t])
            


