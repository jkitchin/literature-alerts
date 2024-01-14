#!/usr/bin/env python
import os
import requests
import datetime
from math import ceil

API_KEY = os.environ['OPENALEX_API_KEY']

today = datetime.date.today()
week_ago = (today - datetime.timedelta(weeks=2)).strftime("%Y-%m-%d")

url = f'https://api.openalex.org/works?filter=author.id:https://openalex.org/A5054680242,from_created_date:{week_ago}&api_key={API_KEY}'

data = requests.get(url).json()
count = data['meta']['count']
perpage = data['meta']['per_page']
npages = ceil(count / perpage)

def process_result(result):
    authors = ', '.join([au['author']['display_name'] for au in result['authorships'] ])
    return f'''** {result['title']}
:PROPERTIES:
:ID: {result['id']}
:DOI: {result['doi']}
:AUTHORS: {authors}
:HOST: {result['primary_location']['source']['display_name']}    
:END:

'''

# Process page 1
s = ''
for result in data['results']:
    s += process_result(result)

for i in range(1, npages):
    purl = url + f'&page={i}'
    data = requests.get(url).json()
    for result in data['results']:
        s += process_result(result)
  
    
with open('results.dat', 'wa') as f:
    f.write(s)
