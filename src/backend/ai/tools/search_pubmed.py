import requests
import xmltodict
import traceback
import asyncio

def search_pubmed_article(query: str, 
                          max_results: int = 10, 
                          content_size: int|None=None,
                          api_key: str='') -> list:
    """Returns a list of pubmed reference and article content for a given query"""
    
    # def doi2apa(doi):
    #     url = f'http://dx.doi.org/{doi}'
    #     response = requests.get(url, headers={'accept':'text/x-bibliography; style=apa'})
    #     if not response.ok: raise Exception(response.text)
    #     return response.text.strip()
        
    # def getPubMedArticle(pmcid):

    #     url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC{pmcid}/unicode'
    #     response = requests.get(url)
    #     if not response.ok: raise Exception(response.text)
    #     try:
    #         return response.json()
    #     except:
    #         raise Exception(response.text)
        
    # def getPubMedArticlePubtator(pmid):
    #     url = f'https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson?pmids={pmid}&full=true'
    #     response = requests.get(url)
    #     if not response.ok: raise Exception(response.text)
    #     try:
    #         return response.json()
    #     except:
    #         raise Exception(response.text)
        
    # def getArticleBioC(pmcid):

    #     exclude_sections: list=['REF', 'METHODS', 'RESULTS']

    #     d = getPubMedArticle(pmcid=pmcid)
    #     passages = d[0]['documents'][0]['passages']
    #     doi = passages[0]['infons']['article-id_doi']

    #     # d = getPubMedArticlePubtator(pmid=pmid)
    #     # passages = d['PubTator3'][0]['passages']
    #     # if 'journal' in passages[0]['infons']:
    #     #     doi = passages[0]['infons']['journal'].split('doi:')[-1].split('. ')[0].strip()
    #     # elif 'article-id_doi' in passages[0]['infons']:
    #     #     doi = passages[0]['infons']['article-id_doi']
    #     # else:
    #     #     raise Exception('DOI could not be found')

    #     ref = doi2apa(doi)

    #     section_type, section_content = '', ''
    #     content = '' 
    #     for item in passages[1:] + [{'infons': {'section_type': '', 'type': ''}, 'text': ''}]:

    #         if item['infons']['section_type'] in exclude_sections : continue
    #         if section_type != item['infons']['section_type']:
    #             if section_type != '' and section_content != '':
    #                 content += (('\n\n\n' if content != '' else '') + f'**{section_type}**\n\n{section_content}')
    #         section_type = item['infons']['section_type']
    #         section_content += f'\n*{item['text']}*\n' if 'title' in item['infons']['type'] else item['text']

    #     return ref, content
    
    
    def getPubMedArticleEutils(pmcid):
        url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&rettype=full&api_key={api_key}'
        response = requests.get(url)
        if not response.ok: raise Exception(response.text)
        try:
            return xmltodict.parse(response.text)
        except:
            raise Exception(response.text)
        
    def getArticleEutils(pmcid):

        def parseText(d_xml, text = []):
            
            text = text.copy()
            
            if isinstance(d_xml, dict):
                for k in d_xml:
                    if k not in ['title', 'sec', 'p', '#text']: continue
                    text = parseText(d_xml[k], text=text)
            elif isinstance(d_xml, list):
                for k in d_xml:
                    text = parseText(k, text=text)
            else:
                if d_xml: text.append(d_xml)

            return text
        
        def parseTextField(val):
            if isinstance(val, dict):
                return val.get('#text', '')
            return val

        try:
            d = getPubMedArticleEutils(pmcid=pmcid)
        except Exception as exp:
            raise Exception(f'In getPubMedArticleEutils(pmcid={pmcid}), Line number: {exp.__traceback__.tb_lineno}, Description: {exp}\n\n{traceback.format_exc()}')
            
        assert 'front' in d['pmc-articleset']['article'], 'Reference not available'
        assert 'body' in d['pmc-articleset']['article'], 'Content not available'
        
        ref = {'pmcid': pmcid}

        front = d['pmc-articleset']['article']['front']

        ref['journal'] = parseTextField(front['journal-meta']['journal-title-group']['journal-title'])
        
        for article_id in front['article-meta']['article-id']:
            ref[article_id['@pub-id-type']] = article_id['#text'].strip()
            
        assert 'doi' in ref, 'DOI not found'

        ref['title'] = parseTextField(front['article-meta']['title-group']['article-title'])
    
        authors = []
        contrib_group = front['article-meta']['contrib-group']
        if isinstance(contrib_group, list):
            for contrib_group_element in contrib_group:
                if isinstance(contrib_group_element['contrib'], list):
                    for contrib in contrib_group_element['contrib']:
                        if contrib['@contrib-type'] == 'author':
                            authors.append({'first_name': contrib['name']['given-names']['#text'].strip(), 
                                            'last_name': contrib['name']['surname'].strip()})
        elif isinstance(contrib_group['contrib'], list):
            for contrib in contrib_group['contrib']:
                if contrib['@contrib-type'] == 'author':
                    authors.append({'first_name': contrib['name']['given-names']['#text'].strip(), 
                                    'last_name': contrib['name']['surname'].strip()})
        else:
            if contrib_group['contrib']['@contrib-type'] == 'author':
                if 'collab' in contrib_group['contrib']:
                    authors.append({'first_name': '', 
                                    'last_name': contrib_group['contrib']['collab'].strip()})

        ref['authors'] = authors

        if isinstance(front['article-meta']['pub-date'], list):
            for pub_date in front['article-meta']['pub-date']:
                ref['year'] = pub_date['year']
                break
        else:
            ref['year'] = front['article-meta']['pub-date']['year']

        ref['year'] = parseTextField(ref['year'])
        ref['volume'] = parseTextField(front['article-meta'].get('volume', ''))
        ref['issue'] = parseTextField(front['article-meta'].get('issue', ''))
        
        if 'elocation-id' in front['article-meta']:
            ref['pages'] = front['article-meta']['elocation-id']
        else:
            ref['pages'] = f'{front['article-meta']['fpage']}-{front['article-meta']['lpage']}'

        ref['pages'] = parseTextField(ref['pages'])

        abstract = front['article-meta']['abstract']
        body = d['pmc-articleset']['article']['body']
        
        abstract = ' '.join(parseText(abstract))
        body = ' '.join(parseText(body))
        
        return ref, abstract, body
    
    def searchLiterature(query, retstart=1, retmax=5):
        qstring = f'db=pmc&term={query}&sort=relevance&retstart={retstart}&retmax={retmax}&api_key={api_key}'
        url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{qstring}'
        response = requests.get(url)
        if not response.ok: raise Exception(response.text)
        try:
            return xmltodict.parse(response.text)
        except:
            raise Exception(response.text)

    print(query)

    try:
        res = searchLiterature(query)
        ids = res['eSearchResult']['IdList']

        if not ids: return []
        ids = ids['Id']
        if isinstance(ids, str): ids = [ids]
    except Exception as exp:
        print(f'In searchLiterature("{query}"): {str(exp)}')
        return []
    
    res = []
    for id in ids:
        try:
            ref, abstract, body = getArticleEutils(pmcid=id)
        except Exception as exp:
            print(f'In getArticleEutils(pmcid={id}):, Line number: {exp.__traceback__.tb_lineno}, Description: {exp}\n\n{traceback.format_exc()}')
            continue

        if content_size is not None: body = body[:content_size]
        
        res.append({"ref": ref, "abstract": abstract, "body": body})

        if len(res) >= max_results: break

    return res

async def search_pubmed_article_async(*args, **kargs):

    return search_pubmed_article(*args, **kargs)


def formatAPA(ref):

    # Author, A. A., Author, B. B., & Author, C. C. (Year). Title of article. Journal Title, volume(issue), page numbers. DOI or URL.

    authors = []
    for author in ref['authors']:
        if author['first_name']:
            authors.append(f'{author['last_name']}, {' '.join([f'{item[0]}.' for item in author['first_name'].split(' ')])}')
        else:
            authors.append(author['last_name'])
    
    if len(authors) > 10:
        authors = authors[:5] + ['et al.']

    if ref['volume'] and ref['issue']:
        vol_issue_pages = f'{ref['volume']}({ref['issue']}), {ref['pages']}'
    elif ref['volume']:
        vol_issue_pages = f'{ref['volume']}, {ref['pages']}'
    else:
        vol_issue_pages = f'{ref['pages']}'
    
    return f'{', '.join(authors)} ({ref['year']}). {ref['title']}. {ref['journal']}, {vol_issue_pages}. http://doi.org/{ref['doi']}'