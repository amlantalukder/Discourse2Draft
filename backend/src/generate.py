import logging

from .utils import print_func_name
from .manage_outline import SpecialSectionTypes, ContentTypes
from .common import getLiteraturesFromDB, sanitizeContent, processCitation
from .ai.architecture import AbstractSectionDetectorArchitecture, \
                            ContentWriterArchitecture, \
                            AbstractWriterArchitecture, \
                            OutlineCreatorArchitecture

# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
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
    
    response = await agent.ainvoke({'content_pre_summary': content_pre_summary, 
                                    'current_section': current_section,
                                    'content_specific_instructions': instructions})
    
    content, content_summary, concept_map = response['content'], response.get('content_summary'), response.get('concept_map', {})
        
    attached_references_ai = response.get('references', {})
    attached_references = getSanitizedReferences(attached_references_ai, attached_references)

    if attached_references:
        content_for_frontend, ref_list = processCitation(content, attached_references, ref_list, enable_html_link_format=True)
    else:
        content_for_frontend = content

    return content, content_summary, concept_map, ref_list, sanitizeContent(content_for_frontend)

# ---------------------------------------------------------------------------
@print_func_name
async def generateOutline(agent: OutlineCreatorArchitecture, query: str, details: str = ''):
    
    response = await agent.ainvoke({'query': query, 'details': details})
    return response['content']