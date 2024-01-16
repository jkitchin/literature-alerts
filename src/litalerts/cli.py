import click
import datetime
from yaml import load, Loader

from .openalex import run_query
from .org import write_org
from .rss import write_rss

@click.command()
@click.option('-f', '--fname', default='queries.yml', help='yml file with queries')              
@click.option('-s', '--since', default=7, help='days since')
def cli(fname, since):

    today = datetime.date.today()
    _since = (today - datetime.timedelta(days=since)).strftime("%Y-%m-%d")

    with open(fname, 'r') as f:
        queries = load(f.read(), Loader=Loader)

    for topic in queries['queries']:
        topic['today'] = today
        topic['since'] = _since
        
        results = run_query(topic, _since)
        write_org(topic, results)
        write_rss(topic, results)
