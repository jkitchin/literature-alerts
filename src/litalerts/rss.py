from rfeed import Item, Feed, Guid
from pathlib import Path
import lxml.etree as etree
from io import BytesIO
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


def get_rss_item(topic, result):
    """Return an RSS Item for RESULT.
    RESULT is a json object for a work.
    """
    authors = ', '.join([au['author']['display_name'] for au in result['authorships'] ])
    word_index = []

    aii = result.get('abstract_inverted_index', None)

    if aii:
        for k,v in aii.items():
            for index in v:
                word_index.append([k, index])

        word_index = sorted(word_index,key = lambda x : x[1])
        abstract = ' '.join([x[0] for x in word_index])
    else:
        abstract = 'No abstract'

    source = result.get('primary_location', {}).get('source', {})
    if source:
        host = source.get('display_name', 'No host')
    else:
        host = 'No host'

    citation = f"{authors}, {host}. {result.get('biblio', {}).get('volume', 0)}({result.get('biblio', {}).get('issue', 0)})] {result['publication_year']}."
        
    return Item(title = f'[{topic["label"]}] {result["title"]}',
                description=citation + '\n' + abstract,
                author=authors,
                link=result['doi'],
                guid=Guid(result['doi']),
                pubDate=datetime.datetime.strptime(result['publication_date'], "%Y-%m-%d"))


def write_rss(topic, results):
    print('rss:', topic, results)

    items = [get_rss_item(topic, result) for result in results]
    
    base = '-'.join(topic['label'].split())    
    rssfile = Path('rss') / (base + '.xml')
    feed = Feed(title=topic['label'],
                link=f'https://raw.githubusercontent.com/jkitchin/literature-alerts/main/{rssfile}',
                description=topic.get('description', 'no description'),
                language='en-US',
                lastBuildDate = datetime.datetime.now(),
                items=[get_rss_item(topic, result) for result in items])


    rlogger = logging.getLogger("RSS Log")
    rlogger.setLevel(logging.INFO)
    rhandler = TimedRotatingFileHandler(rssfile,
                                       when="w0",
                                       interval=1)
    rlogger.addHandler(rhandler)
        
    # this just pretty prints the file
    xml = etree.parse(BytesIO(f"{feed.rss()}".encode('utf-8')))
    pxml = etree.tostring(xml,
                          pretty_print=True).decode('utf-8')
    rlogger.info(pxml)   
    
