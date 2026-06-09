import logging
import re

from .utils import print_func_name
from .manage_outline import SpecialSectionTypes, ContentTypes
from .common import formatCitations
from .db import selectFromDB, vector_db_collections_type
from .ai.architecture import AbstractSectionDetectorArchitecture, ContentWriterArchitecture, AbstractWriterArchitecture
from .ai.tools.search_pubmed import formatAPA

@print_func_name
def getLiteraturesFromDB(literature_id_list):

    literature_records = selectFromDB(table_name='literature',
                                    field_names=['id'],
                                    field_values=[literature_id_list])
    
    assert not literature_records.empty, f"No literature record found with id: {literature_id_list}"

    literature_records['authors'] = literature_records['authors'].map(eval)
    literature_records['reference'] = literature_records.apply(lambda x: formatAPA(dict(x[['authors', 'title', 'year', 'journal', 'volume', 'issue', 'pages', 'doi', 'pmid']])), axis=1)
    literature_records['type'] = vector_db_collections_type.LITERATURE.value
    
    literature_info = list(literature_records[['id', 'reference', 'type']].values)

    literature_records['doi'] = literature_records['id']
    file_info = literature_records[['id', 'authors', 'title', 'journal', 'volume', 'issue', 'pages', 'year', 'doi']].set_index('id').T.to_dict()

    return literature_info, file_info

@print_func_name
def findAbstractSection(agent_abstract_detector: AbstractSectionDetectorArchitecture, d_outline: dict) -> tuple[dict, str]:
    '''
    Returns the header of an abstract section (if the outline has abstract) 
    or an empty string (if the outline does not have abstract)
    '''

    @print_func_name
    def isThisAbstract(section_header):
        response = agent_abstract_detector.invoke({'current_section': section_header})
        return d_outline, response[ContentTypes.IS_ABSTRACT.value]
    
    if not d_outline: return d_outline, ''

    title = next(iter(d_outline))
    first_section_header = next(iter(d_outline[title]))
    
    content = d_outline[title][first_section_header][SpecialSectionTypes.CONTENT.value]
    if len(content) > 0 and content[0][0] == ContentTypes.IS_ABSTRACT.value:
        return d_outline, first_section_header
    
    if isThisAbstract(first_section_header): 
        d_outline[title][first_section_header][SpecialSectionTypes.CONTENT.value].insert(0, (ContentTypes.IS_ABSTRACT.value, True))
        return d_outline, first_section_header
    
    return d_outline, ''

@print_func_name
def getSanitizedReferences(references_ai, attached_references):

    lit_ids = []
    for ref_id, _ in references_ai.items():
        if ref_id not in attached_references:
            lit_ids.append(ref_id)

    if lit_ids:
        try: 
            refs, _ = getLiteraturesFromDB(lit_ids)
            attached_references |= {str(k): v for k, v, _ in refs}
        except Exception as exp:
            logging.error(exp)

    return attached_references

@print_func_name
def processCitation(content, ref_list, attached_references):

    content = formatCitations(content)

    ref_groups = re.findall(r'CITE\(([\w\W]+?)\)', content)

    refs_seen = set()
    d_ref = {}
    for refs in ref_groups:
        refs = re.sub(r'\),\ *CITE\(', ', ', refs)
        if refs in refs_seen: continue
        refs_seen.add(refs)
        ref_links = []
        for ref in refs.split(','):
            ref = ref.strip()
            if ref not in attached_references: 
                logging.warning(f'{ref} not found in reference list, skipping...')
                continue
            if ref in d_ref:
                ref_links.append(d_ref[ref])
                continue
            try:
                d_ref[ref] = ref_list.index(attached_references[ref]) + 1
            except ValueError:
                ref_list.append(attached_references[ref])
                d_ref[ref] = len(ref_list)
            
            ref_links.append(d_ref[ref])
        
        ref_links = sorted(ref_links)

        if len(ref_links) > 2 and len(ref_links) == (ref_links[-1]-ref_links[0]+1):
            new_citation = f'<a href="#:~:text=References">{ref_links[0]}-{ref_links[-1]}</a>'
        else:
            new_citation = f'{', '.join([f'<a href="#:~:text=References">{ref_cite}</a>' for ref_cite in sorted(ref_links)])}'
        if new_citation == '':
            logging.warning(f'Invalid citation(s) or citation(s) not found in database: [CITE({refs})], removing ...')
            content = re.sub(rf' *\[CITE\({refs}\)\]', new_citation, content)
        else:
            content = content.replace(f'CITE({refs})', new_citation)

    if 'CITE' in content: breakpoint()

    return content, ref_list

@print_func_name
def sanitizeContent(content):
    return re.sub(r' \~([^\~])', r' \\~\1', content)

@print_func_name
async def generateContent(agent: ContentWriterArchitecture | AbstractWriterArchitecture,
                          content_pre_summary: str, 
                          current_section: str, 
                          instructions: str,
                          ref_list: list[str], 
                          attached_references: dict[str, str]):
    
    '''
    Generates content for a section using the provided agent, and processes the citations in the generated content.

    Args:
        agent: The agent to use for content generation. Can be an instance of ContentWriterArchitecture or AbstractWriterArchitecture.
        content_pre_summary: A summary of the content to be generated, which may be used by the agent to generate the content.
        current_section: The header of the section for which content is being generated.
        instructions: Any specific instructions to be followed for content generation.
        ref_list: A list of references that have been attached to the outline so far. This list may be updated if the generated content contains citations that are not in the attached_references.
        attached_references: A dictionary mapping reference IDs to their formatted reference strings collected from the database that have been attached to the generated file, but may not have been included in ref_list yet.
    '''
    
    response = await agent.ainvoke({'content_pre_summary': content_pre_summary, 
                                    'current_section': current_section,
                                    'content_specific_instructions': instructions})
    
    content, content_summary, concept_map = response['content'], response.get('content_summary'), response.get('concept_map', {})
        
    attached_references_ai = response.get('references', {})
    attached_references = getSanitizedReferences(attached_references_ai, attached_references)

    if attached_references:
        content_for_frontend, ref_list = processCitation(content, ref_list, attached_references)
    else:
        content_for_frontend = content

    return content, content_summary, concept_map, ref_list, sanitizeContent(content_for_frontend)