"""Create org files."""
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler


def get_org_item(topic, result):
    """Get an org string for RESULT.
    RESULT will be a json item for a Work.
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

    ologger = logging.getLogger("ORG + " + topic['label'])
    ologger.setLevel(logging.INFO)
    ohandler = TimedRotatingFileHandler(orgfile,
                                       when="w0",
                                       interval=1)
    ologger.addHandler(ohandler)
    ologger.info(s)
