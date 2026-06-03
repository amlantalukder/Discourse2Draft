import json
import re
import logging
import datetime
from pathlib import Path
from docx import Document

from .utils import Config, print_func_name
from .manage_outline import SpecialSectionTypes, ContentTypes
from .db import selectFromDB, insertIntoDB, updateDB, uploaded_files_status

@print_func_name
def getDocContent(file_id, attached_files=[], file_info={}):

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

    attached_references = {str(k): v for k, v, _ in attached_files}
    content_md, content_docx, content_tex, ref_list, used_files_info= extractContentFromOutline(d_outline)
    
    if attached_files:
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
def uploadFiles(files, email='', session_id=''):

    for file in files:

        current_time = datetime.now()
        
        if email != '':
            records = selectFromDB(table_name='uploaded_files', 
                            field_names=['email', 'file_name', 'status'],
                            field_values=[[email], [file['name']], [uploaded_files_status.UPLOADED.value]])
        else:
            records = selectFromDB(table_name='uploaded_files', 
                            field_names=['session', 'file_name', 'status'],
                            field_values=[[session_id], [file['name']], [uploaded_files_status.UPLOADED.value]])
        
        if records.empty:

            ids = insertIntoDB(table_name='uploaded_files', 
                        field_names=['email', 'session', 'file_name', 'status', 'create_date', 'update_date'], 
                        field_values=[[email], [session_id], [file['name']], [uploaded_files_status.UPLOADED.value], [current_time], [current_time]])
            uploaded_file_id = int(ids[0])
            
        else:
            updateDB(table_name='uploaded_files', 
                    update_fields=['status', 'update_date'], 
                    update_values=[uploaded_files_status.UPLOADED.value, current_time], 
                    select_fields=['id'], 
                    select_values=[list(map(int, records.id.values))])
            uploaded_file_id = int(records.iloc[0].id)

        # ids = insertIntoDB(table_name='uploaded_files', 
        #                    field_names=['email', 'session', 'file_name', 'status', 'create_date', 'update_date'], 
        #                    field_values=[[email], [session_id], [file['name']], [uploaded_files_status.UPLOADED.value], [current_time], [current_time]])
        # uploaded_file_id = ids[0]
            
        dir_uploaded_files = Config.DIR_CONTENTS / 'uploaded_docs'
        dir_uploaded_files.mkdir(parents=False, exist_ok=True)

        with open(dir_uploaded_files / f'{uploaded_file_id}{Path(file['datapath']).suffix}', 'wb') as fp:
            with open(file['datapath'], 'rb') as fp_r:
                fp.write(fp_r.read())

@print_func_name
def unMarkdownText(text):

    from bs4 import BeautifulSoup
    from markdown import markdown

    html = markdown(text)
    return ''.join(BeautifulSoup(html).findAll(text=True))

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