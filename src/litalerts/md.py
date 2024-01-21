"""Create org files."""
import time
from pathlib import Path
import urllib.parse

from .openalex import (get_authors,  get_md_authors,
                       get_abstract, get_host,
                       get_citation, get_md_citation,
                       html_to_text)


def get_md_item(topic, result):
    """Get a Markdown string for RESULT.
    RESULT will be a json item for a Work.
    """
    authors = get_md_authors(result)
    host = get_host(result)
    abstract = get_abstract(result)
    citation = get_md_citation(result)

    _pdf = result['primary_location'].get('pdf_url', None)
    if _pdf:
        pdf = f' ([pdf]({_pdf}))'
    else:
        pdf = ''
    isoa = result['primary_location'].get('is_oa', False)

    return f'''## {html_to_text(result['title'])}   

OpenAlex: {result['id']}    
Open access: {isoa}
    
{citation}{result['doi']}{pdf}.
    
{abstract}    

    
'''


def write_md(topic, results):
    """Given a TOPIC and RESULTS, write them out to a Markdown file.
    """

    s = '\n'.join([get_md_item(topic, result) for result in results])
    base = '-'.join(topic['label'].split())
    Path('md').mkdir(exist_ok=True)
    mdfile = Path('md') / (base + '.md')
    print(f'writing to {mdfile}')
    
    with open(mdfile, 'w') as f:        
        f.write(f'# {topic["label"]}\n')
        f.write(f'Description: {topic["description"]}\n')
        f.write(f'Created on {time.asctime()}\n\n')
        f.write(f'Found {len(results)} results from {topic["since"]} to {topic["today"]}\n')
        f.write('OpenAlex URLS (not including from_created_date or the API key)\n')
        for _filter in topic['filter']:
            furl = f'https://api.openalex.org/works?filter={urllib.parse.quote(_filter)}'
            f.write(f'- [{furl}]({furl})\n')
        f.write('\n')
        f.write(s)
        

    
