#!/usr/bin/env python
import os
import sys
import requests
import datetime
from math import ceil
import datetime
from rfeed import Item, Feed, Guid
from dotenv import load_dotenv
from yaml import load, Loader
import urllib.parse
import hashlib
from pathlib import Path

# This does nothing if there is no .env
load_dotenv() 

API_KEY = os.environ['OPENALEX_API_KEY']

today = datetime.date.today()
day_ago = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

with open('queries.yml', 'r') as f:
    queries = load(f.read(), Loader=Loader)

    print(queries)
    
API = 'https://api.openalex.org/works?filter='
 
def process_result(result):
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

    return f'''** [{topic["label"]}] {result['title']}
:PROPERTIES:
:ID: {result['id']}
:DOI: {result['doi']}
:AUTHORS: {authors}
:HOST: {host}
:END:
    
[[elisp:(doi-add-bibtex-entry "{result['doi']}")][Get bibtex entry]] 

- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--referenced-works "{result['id']}"))][Get references]]
- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--related-works "{result['id']}"))][Get related work]]
- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--cited-by-works "{result['id']}"))][Get cited by]]

OpenAlex: {result['id']}
    
{authors}, {host}. {result['doi']}
    
{abstract}    

    
'''

def get_rss_item(result):
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

    

# Process page 1
s = ''
RSS_ITEMS = []

for topic in queries['queries']:
    for _filter in topic['filter']:
        print(f'Running {_filter}')
        url = (API + urllib.parse.quote(_filter)
               + f',from_created_date:{day_ago}&api_key={API_KEY}')

        data = requests.get(url).json()

        count = data['meta']['count']
        perpage = data['meta']['per_page']
        npages = ceil(count / perpage)

        print(f"  Found {len(data['results'])} results")
        
        for result in data['results']:
            s += process_result(result)
            RSS_ITEMS += [get_rss_item(result)]

        for i in range(1, npages):
            purl = url + f'&page={i}'
            data = requests.get(url).json()
            for result in data['results']:
                s += process_result(result)
                RSS_ITEMS += [get_rss_item(result)]


# Touch a flagfile for making an issue.                
if s != '':
    Path('MAKEISSUE').touch()

with open('results.org', 'w') as f:
    f.write(f'* Results for {day_ago}\n\n')
    f.write(s)


feed = Feed(title='OA literature alerts',
            link='https://raw.githubusercontent.com/jkitchin/literature-alerts/main/rss.xml',
            description='Proof of concept RSS feed',
            language='en-US',
            lastBuildDate = datetime.datetime.now(),
            items=RSS_ITEMS)

with open('rss.xml', 'w') as f:
    f.write(feed.rss())

import lxml.etree as etree

x = etree.parse('rss.xml')
with open('rss.xml', 'w') as f:
    f.write(etree.tostring(x, pretty_print=True).decode('utf-8'))
