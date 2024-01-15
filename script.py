#!/usr/bin/env python
import os
import sys
import requests
import datetime
from math import ceil
import datetime
from rfeed import Item, Feed, Guid


API_KEY = os.environ['OPENALEX_API_KEY']

today = datetime.date.today()
day_ago = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

url = f'https://api.openalex.org/works?filter=title_and_abstract.search:oxygen+evolution,from_created_date:{day_ago}&api_key={API_KEY}'

data = requests.get(url).json()

count = data['meta']['count']
perpage = data['meta']['per_page']
npages = ceil(count / perpage)

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

    return f'''** {result['title']}
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
    return Item(title = result['title'],
                description=abstract,
                author=authors,
                link=result['doi'],
                guid=Guid(result['doi']),
                pubDate=datetime.datetime.strptime(result['publication_date'], "%Y-%m-%d"))

    

# Process page 1
s = ''
RSS_ITEMS = []
for result in data['results']:
    s += process_result(result)
    RSS_ITEMS += [get_rss_item(result)]

for i in range(1, npages):
    purl = url + f'&page={i}'
    data = requests.get(url).json()
    for result in data['results']:
        s += process_result(result)
        RSS_ITEMS += [get_rss_item(result)]
        
     
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
