import json
import re
import logging
from docx import Document
from enum import Enum

from .utils import Config, print_func_name
from .vectordb import ChromaDB
from .db import selectFromDB, vector_db_collections_status, vector_db_collections_type
from .ai.tools.search_pubmed import formatAPA

# ---------------------------------------------------------------------------
class OutlineTAGs(Enum):
    INSTRUCTIONS_START = '[--instructions--]'
    INSTRUCTIONS_END = '[/--instructions--]'
    CONTENT = '[--content--]'

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
def formatCitations(text):
    '''
    Convert [CITE(abc), CITE(bcd), CITE(cde)] to [CITE(abc, bcd, cde)]
    '''
    pattern = r'\[(?:CITE\([^)]+\)(?:,\s*)?)+\]'
    
    def replace_func(match):
        # Extract all citations
        citations = re.findall(r'CITE\(([^)]+)\)', match.group(0))
        # Rebuild as single CITE with all arguments
        return f'[CITE({", ".join(citations)})]'
    
    return re.sub(pattern, replace_func, text)

@print_func_name
def getDocContent(file_id, vector_db_collections_id_uploaded_files, vector_db_collections_id_literature):

    @print_func_name
    def processCitation(content, ref_list=[], used_files_info={}):

        content = formatCitations(content)

        content_tex = content
        
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
                    used_files_info[ref] = file_info[ref]

                ref_links.append(d_ref[ref])
        
            ref_links = sorted(ref_links)
            if len(ref_links) > 2 and len(ref_links) == (ref_links[-1]-ref_links[0]+1):
                new_citation = f' [{ref_links[0]}-{ref_links[-1]}]'
            else:
                new_citation = f' [{', '.join(map(str, ref_links))}]'
            
            content = content.replace(f'[CITE({refs})]', new_citation)
            content_tex = content_tex.replace(f'[CITE({refs})]', f'\\cite{{{refs}}}')
    
        return content, content_tex, ref_list, used_files_info

    @print_func_name
    def extractContentFromOutline(d, content_md=[], content_docx=Document(), content_tex=[], ref_list=[], used_files_info={}, level=1):

        def latexLevels(level, header):

            match level:
                case 1:
                    return f'\\title{{{header}}}'
                case 2:
                    return f'\\section{{{header}}}'
                case 3:
                    return f'\\subsection{{{header}}}'
                case 4:
                    return f'\\subsubsection{{{header}}}'
                case 5:
                    return f'\\paragraph{{\\textbf{{{header}}}}}'
                case 6:
                    return f'\\paragraph{{\\textit{{{header}}}}}'

        if not isinstance(d, dict):
            for k, v in d:
                if k not in [ContentTypes.CONTENT_AI.value, ContentTypes.CONTENT_USER.value]: continue
                content_text, content_tex_text, ref_list, used_files_info = processCitation(v, ref_list, used_files_info)
                content_md.append(content_text)
                content_docx.add_paragraph(content_text)
                content_tex.append(content_tex_text)
        else:
            for k in d:
                if k != SpecialSectionTypes.CONTENT.value:
                    content_docx.add_heading(k, level=level)
                    content_md, content_docx, content_tex, ref_list, used_files_info = extractContentFromOutline(d[k], 
                                                                                                                 content_md + [f'{'#' * level} {k}'], 
                                                                                                                 content_docx, 
                                                                                                                 content_tex + [latexLevels(level, k)], 
                                                                                                                 ref_list, used_files_info, level+1)
                else:
                    content_md, content_docx, content_tex, ref_list, used_files_info = extractContentFromOutline(d[k], 
                                                                                                                 content_md, 
                                                                                                                 content_docx, 
                                                                                                                 content_tex, 
                                                                                                                 ref_list, used_files_info, level+1)

        return content_md, content_docx, content_tex, ref_list, used_files_info
    
    @print_func_name
    def convertToLatex(content):
        def formatLatex(text):

            """Escapes special characters in a string for LaTeX compatibility."""
            latex_special_chars = {
                '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '<': r'$<$', '>': r'$>$'
            }
            for char, replacement in latex_special_chars.items():
                text = text.replace(char, replacement)

            return text

        if not len(content): return ''
        return f"\\documentclass{{article}}\n\n{formatLatex(content[0])}\n\n\\begin{{document}}\n\n\\maketitle\n\n{formatLatex('\n'.join(content[1:]))}\n\n\\bibliographystyle{{plain}}\n\n\\bibliography{{bibliography}}\n\n\\end{{document}}"
    
    @print_func_name
    def getBibFormat(file_info):

        bib_text = ''
        for k, v in file_info.items():
            bib_ele = []
            for k1, v1 in v.items():
                if k1 == 'authors':
                    authors = [f'{author['first_name']} {author['last_name']}' for author in v1]
                    bib_ele.append(f'author = "{', '.join(authors)}"')
                elif k1 == 'pages':
                    bib_ele.append(f'{k1} = "{v1.replace('-', '--')}"')
                else:
                    bib_ele.append(f'{k1} = "{v1}"')
            bib_text += f'@article{{{k},\n\t{',\n\t'.join(bib_ele)}\n}}\n\n'

        return bib_text

    outline_file_path = Config.DIR_CONTENTS / f'outline_{file_id}.json'

    with open(outline_file_path) as fp:
        d_outline = json.load(fp)

    attached_references, file_info = getAttachedRefs(vector_db_collections_id_uploaded_files, vector_db_collections_id_literature)

    attached_references = {str(k): v for k, v, _ in attached_references}
    content_md, content_docx, content_tex, ref_list, used_files_info= extractContentFromOutline(d_outline)
    
    if attached_references:
        content_md.append('## References')
        content_docx.add_heading('References', level=2)
        for i, ref in enumerate(ref_list):
            content_md.append(f'\n[{i+1}] {ref}')
            content_docx.add_paragraph(f'[{i+1}] {ref}')
        bibs = getBibFormat(used_files_info)
    else:
        bibs = ''

    content_md = '\n'.join(content_md)
    content_tex = convertToLatex(content_tex)

    return content_md, content_docx, content_tex, bibs

@print_func_name
def createVectorDBCollection(collection_name: str, replace_collection: bool=True):

    db = ChromaDB()
    if replace_collection: 
        db.create(collection_name=collection_name, delete_if_exists=True)
    else:
        db.get(collection_name=collection_name)

    return db

@print_func_name
def getLiteraturesFromDB(literature_id_list):

    literature_records = selectFromDB(table_name='literature',
                                    field_names=['id'],
                                    field_values=[literature_id_list])
    
    literature_records['authors'] = literature_records['authors'].map(eval)
    literature_records['reference'] = literature_records.apply(lambda x: formatAPA(dict(x[['authors', 'title', 'year', 'journal', 'volume', 'issue', 'pages', 'doi', 'pmid']])), axis=1)
    literature_records['type'] = vector_db_collections_type.LITERATURE.value
    
    literature_info = list(literature_records[['id', 'reference', 'type']].values)

    literature_records['doi'] = literature_records['id']
    file_info = literature_records[['id', 'authors', 'title', 'journal', 'volume', 'issue', 'pages', 'year', 'doi']].set_index('id').T.to_dict()

    return literature_info, file_info

@print_func_name
def getVectorDBFiles(vector_db_collections_id):

    if not vector_db_collections_id: return [], {}

    vector_db_collection_records = selectFromDB(table_name='vector_db_collections', 
                                                field_names=['id', 'status'], 
                                                field_values=[[vector_db_collections_id], [vector_db_collections_status.ACTIVE.value]])
    
    if vector_db_collection_records.empty: return [], {}
    
    vector_db_collection_files_records = selectFromDB(table_name='vector_db_collection_files', 
                                                field_names=['vector_db_collections_id'], 
                                                field_values=[[vector_db_collections_id]])
    
    if vector_db_collection_files_records.empty: return [], {}

    uploaded_files_id_list = list(map(int, vector_db_collection_files_records['uploaded_files_id'].dropna().values))

    if uploaded_files_id_list: 

        uploaded_files_records = selectFromDB(table_name='uploaded_files',
                                            field_names=['id'],
                                            field_values=[uploaded_files_id_list])
        
        uploaded_files_records['type'] = vector_db_collections_type.UPLOADED_FILES.value
        
        uploaded_files_info = list(uploaded_files_records[['id', 'file_name', 'type']].values)

        uploaded_files_records['id'] = uploaded_files_records['id'].map(str)
        uploaded_files_records['title'] = uploaded_files_records['file_name']

        file_info = uploaded_files_records[['id', 'title']].set_index('id').T.to_dict()

        return uploaded_files_info, file_info 

    literature_id_list = list(vector_db_collection_files_records['literature_id'].dropna().values)

    if literature_id_list:
    
        return getLiteraturesFromDB(literature_id_list)
    
    return [], {}

@print_func_name
def getAttachedRefs(vector_db_collections_id_uploaded_files, vector_db_collections_id_literature):

    files_attached, file_info_attached = getVectorDBFiles(vector_db_collections_id_uploaded_files)
    files_lit, file_info_lit = getVectorDBFiles(vector_db_collections_id_literature)
    
    return files_attached + files_lit, file_info_attached | file_info_lit