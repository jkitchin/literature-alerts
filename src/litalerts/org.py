"""Create org files."""
import time
from pathlib import Path

from .openalex import get_authors, get_abstract, get_host, get_citation


def get_org_item(topic, result):
    """Get an org string for RESULT.
    RESULT will be a json item for a Work.
    """
    authors = get_authors(result)
    host = get_host(result)
    abstract = get_abstract(result)
    citation = get_citation(result)       

    return f'''** [{topic["label"]}] {result['title']}
:PROPERTIES:
:ID: {result['id']}
:DOI: {result['doi']}
:AUTHORS: {authors}
:HOST: {host}
:END:

{citation}
    
[[elisp:(doi-add-bibtex-entry "{result['doi']}")][Get bibtex entry]] 

- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--referenced-works "{result['id']}"))][Get references]]
- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--related-works "{result['id']}"))][Get related work]]
- [[elisp:(progn (xref--push-markers (current-buffer) (point)) (oa--cited-by-works "{result['id']}"))][Get cited by]]

OpenAlex: {result['id']}
    
{authors}, {host}. {result['doi']}
    
{abstract}    

    
'''


def write_org(topic, results):
    """Given a TOPIC and RESULTS, write them out to an org-file.
    """

    s = '\n'.join([get_org_item(topic, result) for result in results])
    base = '-'.join(topic['label'].split())
    orgfile = Path('org') / (base + '.org')

    with open(orgfile, 'w'): as f:
        f.write(f'#+TITLE: {topic["label"]}\n')
        f.write(f'Created at {time.asctime()}\n\n')
        f.write(f'Results from {topic["since"]} to {topic["today"]}\n')
        f.write(s)
        

    
