#!/usr/bin/env python
"""Generate filters for citations to papers by John Kitchin.

Run this periodically (monthly or so) to update it with new papers.
"""

import requests
import yaml
import os
import time

# First get my works api url.
req = requests.get("https://api.openalex.org/authors/https://openalex.org/A5003442464",
                   params={'select': 'works_api_url',
                           'email': 'jkitchin@andrew.cmu.edu',
                           'api_key': os.environ.get('OPENALEX_API_KEY', None)})

works_api_url = req.json()['works_api_url']

# Next retrieve all the works ids
next_cursor = '*'

works = []

while next_cursor:
    req = requests.get(works_api_url,
                      params={'email': 'jkitchin@andrew.cmu.edu',
                              'api_key': os.environ.get('OPENALEX_API_KEY', None),
                              'cursor': next_cursor,
                              'select': 'id'}).json()
    works += [result['id'] for result in req['results']]
    next_cursor = req['meta']['next_cursor']


# split the works into groups of 20    
cites = []
related_to = []

while works:
    subset, works = works[0:20], works[20:]
    cites += ['cites:' + '|'.join(subset)]
    related_to += ['related_to:' + '|'.join(subset)]

# create the dictionary for the query and write it out    
query1 = {'queries': [{'label': 'Papers that cite my papers',
                      'description': 'Citations to my papers',
                      'created': time.asctime(),
                      'filter': cites}]}

with open('my-citations.yaml', 'w') as f:
    f.write(yaml.dump(query1))

# create the dictionary for the query and write it out    
query2 = {'queries': [{'label': 'Related papers to my work',
                       'created': time.asctime(),
                       'description': 'Related papers to my papers',
                       'filter': related_to}]}

with open('my-related.yaml', 'w') as f:
    f.write(yaml.dump(query2))
