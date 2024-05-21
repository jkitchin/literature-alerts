"""Create org files."""
import time
from pathlib import Path
import urllib.parse

from .openalex import (get_authors, get_org_authors, get_abstract, get_host,
                       get_citation, get_org_citation,
                       html_to_text)


def get_org_item(topic, result):
    """Get an org string for RESULT.
    RESULT will be a json item for a Work.
    """
    authors = get_org_authors(result)
    host = get_host(result)
    abstract = get_abstract(result)
    citation = get_org_citation(result)

    _pdf = result['primary_location'].get('pdf_url', None)
    if _pdf:
        pdf = f' ([[{_pdf}][pdf]])'
    else:
        pdf = ''
    isoa = result['primary_location'].get('is_oa', False)

    tags = topic['label'].replace(' ', '_')
    tags = tags.replace('-', '_')

    topics = ', '.join([topic['display_name'] for topic
                        in result['topics']])

    # remove line breaks
    title = result['title'].replace(r'\n', ' ')
    title = title.replace(r'\r', ' ')
    return f'''* {html_to_text(title)}  :{tags}:
:PROPERTIES:
:UUID: {result['id']}
:TOPICS: {topics}
:PUBLICATION_DATE: {result.get('publication_date', None)}
:END:    
    
[[elisp:(doi-add-bibtex-entry "{result['doi']}")][Get bibtex entry]] 

- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--referenced-works "{result['id']}"))][Get references]]
- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--related-works "{result['id']}"))][Get related work]]
- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--cited-by-works "{result['id']}"))][Get cited by]]

OpenAlex: {result['id']} (Open access: {isoa})
    
{citation} {result['doi']} {pdf}
     
{abstract}    

    
'''


def write_org(topic, results):
    """Given a TOPIC and RESULTS, write them out to an org-file.
    """

    s = '\n'.join([get_org_item(topic, result) for result in results])
    base = '-'.join(topic['label'].split())
    Path('org').mkdir(exist_ok=True)
    orgfile = Path('org') / (base + '.org')

    with open(orgfile, 'w') as f:        
        f.write(f'#+TITLE: {topic["label"]}\n')
        f.write(f'Description: {topic["description"]}\n')
        f.write(f'Created on {time.asctime()}\n\n')
        f.write(f'Found {len(results)} results from {topic["since"]} to {topic["today"]}\n')
        f.write('OpenAlex URLS (not including from_created_date or the API key)\n')
        for _filter in topic['filter']:
            f.write(f'- [[https://api.openalex.org/works?filter={urllib.parse.quote(_filter)}]]\n')
        f.write('\n')
        f.write(s)
        

    
