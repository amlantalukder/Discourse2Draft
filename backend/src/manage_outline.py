import re
from enum import Enum

from .ai.architecture import OutlineCreatorArchitecture, OutlineFormatterArchitecture
from .utils import print_func_name

# ---------------------------------------------------------------------------
class SpecialSectionTypes(Enum):
    CONTENT = 'content'
    
# ---------------------------------------------------------------------------
class ContentTypes(Enum):
    IS_ABSTRACT = 'is_abstract'
    INSTRUCTIONS = 'instructions'
    CONTENT_USER = 'content_user'
    CONTENT_AI = 'content_ai'
    CONTENT_PRE_SUMMARY = 'content_pre_summary'
    CONCEPT_MAP = 'concept_map'

@print_func_name
def unMarkdownText(text):

    from bs4 import BeautifulSoup
    from markdown import markdown

    html = markdown(text)
    return ''.join(BeautifulSoup(html).findAll(text=True))

@print_func_name
def resetOutline(d):
    
    for k, v in d.items():
        if k != SpecialSectionTypes.CONTENT.value:
            d[k] = resetOutline(v.copy())
        else:
            for i, [content_type, _] in enumerate(d[SpecialSectionTypes.CONTENT.value]):
                if content_type in [ContentTypes.CONTENT_AI.value, ContentTypes.CONTENT_PRE_SUMMARY.value, ContentTypes.CONCEPT_MAP.value]:
                    d[SpecialSectionTypes.CONTENT.value][i][1] = ''

    return d

@print_func_name
def insertOutline(d, outline_items):

    if len(outline_items) == 1:
        d[SpecialSectionTypes.CONTENT.value] = d.get(SpecialSectionTypes.CONTENT.value, []) + outline_items
        return d
    
    if outline_items[0] not in d:
        d[outline_items[0]] = {}
    
    d[outline_items[0]] = insertOutline(d[outline_items[0]].copy(), outline_items[1:])

    return d

@print_func_name
def processOutline(outline):

    def insertUserContentToOutline(d_outline, outline_items, lines):
        content = '\n'.join(lines).strip()
        pattern_instructions = r'[--instructions--]([\w\W]*?)[\/--instructions--]'
        instructions = re.findall(pattern_instructions, content)
        instructions = '\n'.join(map(lambda x: x.strip(), instructions))
        content = re.sub(pattern_instructions, '', content)
        outline_items_new = outline_items.copy()
        if instructions:
            outline_items_new.append([ContentTypes.INSTRUCTIONS.value, instructions])
        if content:
            outline_items_new.append([ContentTypes.CONTENT_USER.value, content])
        d_outline = insertOutline(d_outline.copy(), outline_items_new)
        return d_outline
    
    d_outline, outline_items = {}, []
    chunks_leading_to_content = outline.split('[--content--]')
    for i, x in enumerate(chunks_leading_to_content):
        x = x.strip()
        if not x.strip(): continue
        lines = []
        for line_x in x.split('\n'):
            line_x = line_x.strip(' ')
            if line_x == '': continue
            if not line_x.startswith('#'):
                lines.append(line_x)
                continue

            if lines:
                d_outline = insertUserContentToOutline(d_outline, outline_items, lines)
                lines = []
            
            hashes = line_x.split()[0]
            header = unMarkdownText(' '.join(line_x.split()[1:])).strip()
            
            if hashes != '#' * len(hashes):
                raise ValueError("'#'s must be followed by a space", type="error")
            
            if len(hashes) > len(outline_items) + 1:
                raise ValueError(f"Expected no more than {len(outline_items) + 1} '#'s before {'\n'.join(lines)}", type="error")
            
            if len(hashes) <= len(outline_items):
                outline_items = outline_items[:len(hashes)-1]

            outline_items.append(header)
            
        if lines: 
            d_outline = insertUserContentToOutline(d_outline, outline_items, lines)
            
        if i < len(chunks_leading_to_content)-1:
            d_outline = insertOutline(d_outline.copy(), outline_items + [[ContentTypes.CONTENT_AI.value, '']])

    return d_outline

@print_func_name
def generateOutlineByAI(query, dir_path_ref_files=None):
    '''
    Use AI to generate outline from a given query
    '''
    agent = OutlineCreatorArchitecture(dir_path_ref_files=dir_path_ref_files)   
    response = agent.invoke({'query': query})
    outline = response['content']

    return outline

@print_func_name
def processOutlineByAI(outline):
    '''
    Use AI to process outline into structured format
    '''
    agent = OutlineFormatterArchitecture()
    response = agent.invoke({'outline_unstructured': outline})
    outline_structured = response['content']
    print(outline_structured)
    
    return outline_structured

@print_func_name
def getRawOutline(d, raw_outline=[], counter=1):

    if not isinstance(d, dict):
        for k, v in d:
            if k in [ContentTypes.CONTENT_PRE_SUMMARY.value, ContentTypes.IS_ABSTRACT.value, ContentTypes.CONCEPT_MAP.value]: continue
            if k == ContentTypes.CONTENT_AI.value:
                raw_outline.append('[--content--]')
            elif k == ContentTypes.INSTRUCTIONS.value:
                raw_outline.append(f'[--instructions--]\n{v}\n[/--instructions--]')
            else:
                raw_outline.append(v)
    else:
        for k in d:
            raw_outline = getRawOutline(d[k], raw_outline + [f'{'#' * counter} {k}'] if k != SpecialSectionTypes.CONTENT.value else raw_outline, counter+1)

    return raw_outline