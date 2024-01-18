from rfeed import Item, Feed, Guid
from pathlib import Path
import lxml.etree as etree
from io import BytesIO
import datetime
import time
from .openalex import get_authors, get_abstract, get_host, get_citation

def get_rss_item(topic, result):
    """Return an RSS Item for RESULT.
    RESULT is a json object for a work.
    """
    authors = get_authors(result)
    abstract = get_abstract(result)
    host = get_host(result)
    citation = get_citation(result)
        
    return Item(title = f'{result["title"]}',
                description=f'''{citation} {result['id']}

                {abstract}''', 
                author=authors,
                link=result.get('doi', None) or result.get('id', "No ID"),
                guid=Guid(result.get('doi', time.asctime())),
                pubDate=datetime.datetime.strptime(result['publication_date'], "%Y-%m-%d"))


def write_rss(topic, results):
    """Write the RSS feed for TOPIC and RESULTS.
    TOPIC comes from the query yaml file.
    RESULTS will be json from an openalex query.
    """
    
    items = [get_rss_item(topic, result) for result in results]
    
    base = '-'.join(topic['label'].split())    
    rssfile = Path('rss') / (base + '.xml')
    feed = Feed(title=topic['label'],
                link=f'https://raw.githubusercontent.com/jkitchin/literature-alerts/main/rss/{rssfile}',
                description=topic.get('description', 'no description'),
                language='en-US',
                lastBuildDate = datetime.datetime.now(),
                items=items)

    xml = etree.parse(BytesIO(f"{feed.rss()}".encode('utf-8')))
    pxml = etree.tostring(xml,
                          pretty_print=True).decode('utf-8')
    
    with open(rssfile, 'w') as f:
        f.write(pxml)   
    
