"""Proof of concept for integration with discord.

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
from discord import SyncWebhook
from .md import get_md_item

load_dotenv()

# This is stored in a github secret or in .env
url = os.environ['DISCORD_WEBHOOK']

webhook = SyncWebhook.from_url(url)

@click.command()
@click.option('-f', '--fname', default='queries.yml', help='yml file with queries')              
@click.option('-s', '--since', default=7, help='days since')
def oa_discord(fname, since):
    """Load FNAME and get results from SINCE.
    FNAME is a yaml file with a set of queries in it. 
    SINCE is the number of days since new items were added.
    """
    
    today = datetime.date.today()
    _since = (today - datetime.timedelta(days=since)).strftime("%Y-%m-%d")

    with open(fname, 'r') as f:
        queries = load(f.read(), Loader=Loader)

    for topic in queries['queries']:
        
        topic['today'] = today
        topic['since'] = _since
        results = run_query(topic, _since)

        for result in results:
            msg = get_md_item(topic, result)
            # Messages seem to be limited to 2000 characters
            webhook.send(msg[0:1980] + ' <truncated> ...')
