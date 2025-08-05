from shiny.express import render, module
from shiny.types import ImgData
from utils import Config, print_func_name
from pathlib import Path
import pandas as pd
from ..backend.db import selectFromDB, updateDB, \
                vector_db_collections_status, \
                vector_db_collections_type, \
                generated_files_status, \
                generated_files_ai_architecture
from ..backend.vectordb import ChromaDB, deleteCollection, getLoader
from ..backend.ai.tools.search_pubmed import formatAPA
from datetime import datetime
import json
import re

@print_func_name
def initProfile(config_app):
    if config_app.email != '':
        records = selectFromDB('settings', 
                    field_names=['email'],
                    field_values=[[config_app.email]],
                    order_by_field_names=['update_date'],
                    order_by_types=['DESC'],
                    limit=1)
    else:
        records = selectFromDB('settings', 
                    field_names=['session'],
                    field_values=[[config_app.session_id]],
                    order_by_field_names=['update_date'],
                    order_by_types=['DESC'],
                    limit=1)

    config_app.settings_id = int(records['id'].iloc[0])
    config_app.llm = records['llm'].iloc[0]
    config_app.temperature = float(records['temperature'].iloc[0])
    config_app.instructions = records['instructions'].iloc[0]

@print_func_name
def getFileType(file_name):

    if Path(file_name).suffix not in ['.docx', '.pdf']:
        return 'txt'
    return Path(file_name).suffix[1:]

@module
def getFileTypeIcon(input, output, session, file_type):
    
    @render.image()
    @print_func_name
    def icon():
        img: ImgData = {"src": str(Config.DIR_HOME / 'www' / 'assets' / f'{file_type}_icon.png'), 
                        "width": "100%"}
        return img
    
@print_func_name
def createVectorDBCollection(collection_name: str, replace_collection: bool=True):

    db = ChromaDB()
    if replace_collection: 
        db.create(collection_name=collection_name, delete_if_exists=True)
    else:
        db.get(collection_name=collection_name)

    return db

@print_func_name
def loadFilesToVectorDBCollection(collection_name: str, file_paths: list[tuple[Path, str]], replace_collection: bool=True, progress=None):

    def loadFiles(file_paths):

        docs = []

        progress_counter = 1

        for file_path, file_name in file_paths:
            
            if progress is not None:
                progress.set(progress_counter, f'Extracting file {progress_counter}')
                progress_counter += 1
            
            loader = getLoader(file_path=file_path)
            
            for doc in loader:
                doc.metadata = {**{'app_file_id': Path(file_path).stem, 'app_file_name': file_name}, **{k: str(v) for k, v in doc.metadata.items()}}
                docs.append(doc)

        if progress is not None:
            progress.set(progress_counter, 'Creating vector db')

        return docs

    docs = loadFiles(file_paths)

    db = createVectorDBCollection(collection_name=collection_name, replace_collection=replace_collection)
    db.add(docs=docs)
    
@print_func_name
def getVectorDBFiles(vector_db_collections_id):

    if vector_db_collections_id is None: return [], {}

    uploaded_files_info, literature_info, file_info = [], [], {}

    vector_db_collection_records = selectFromDB(table_name='vector_db_collections', 
                                                field_names=['id', 'status'], 
                                                field_values=[[int(vector_db_collections_id)], [vector_db_collections_status.ACTIVE.value]])
    
    if vector_db_collection_records.empty: return []
    
    vector_db_collection_files_records = selectFromDB(table_name='vector_db_collection_files', 
                                                field_names=['vector_db_collections_id'], 
                                                field_values=[[int(vector_db_collections_id)]])
    
    if vector_db_collection_files_records.empty: return []

    uploaded_files_id_list = list(map(int, vector_db_collection_files_records['uploaded_files_id'].dropna().values))

    if uploaded_files_id_list: 

        uploaded_files_records = selectFromDB(table_name='uploaded_files',
                                            field_names=['id'],
                                            field_values=[uploaded_files_id_list])
        
        uploaded_files_records['type'] = vector_db_collections_type.UPLOADED_FILES.value
        
        uploaded_files_info = list(uploaded_files_records[['id', 'file_name', 'type']].values)

        uploaded_files_records['id'] = uploaded_files_records['id'].map(str)
        uploaded_files_records['title'] = uploaded_files_records['file_name']

        file_info |= uploaded_files_records[['id', 'title']].set_index('id').T.to_dict()

    
    literature_id_list = list(vector_db_collection_files_records['literature_id'].dropna().values)

    if literature_id_list:
    
        literature_records = selectFromDB(table_name='literature',
                                        field_names=['id'],
                                        field_values=[literature_id_list])
        
        literature_records['authors'] = literature_records['authors'].map(lambda authors: json.loads(authors.replace("'first_name': '", '"first_name": "').replace("'first_name'", '"first_name"').replace("'last_name': '", '"last_name": "').replace("'last_name'", '"last_name"').replace("'}", '"}').replace("',", '",')))
        literature_records['reference'] = literature_records.apply(lambda x: formatAPA(dict(x[['authors', 'title', 'year', 'journal', 'volume', 'issue', 'pages', 'doi', 'pmid']])), axis=1)
        literature_records['type'] = vector_db_collections_type.LITERATURE.value
        
        literature_info = list(literature_records[['id', 'reference', 'type']].values)

        literature_records['doi'] = literature_records['id']
        file_info |= literature_records[['id', 'authors', 'title', 'journal', 'volume', 'issue', 'pages', 'year', 'doi']].set_index('id').T.to_dict()

    return uploaded_files_info + literature_info, file_info

@print_func_name
def detachDocs(generated_files_id, vector_db_collections_id):

    current_time = datetime.now()

    updateDB(table_name='generated_files', 
            update_fields=['ai_architecture', 'update_date'], 
            update_values=[generated_files_ai_architecture.BASE.value, current_time], 
            select_fields=['id'], 
            select_values=[[generated_files_id]])
    
    updateDB(table_name='vector_db_collections', 
                update_fields=['status', 'update_date'],
                update_values=[vector_db_collections_status.DELETED.value, current_time],
                select_fields=['id'], 
                select_values=[[vector_db_collections_id]]) 

    vector_db_collection_name = f'{Config.APP_NAME_AS_PREFIX}_collection_{vector_db_collections_id}'
    deleteCollection(vector_db_collection_name)

@print_func_name
def getGeneratedDocuments(email, session_id):

    valid_file_statuses = {e.value for e in generated_files_status} - {generated_files_status.DELETED.value}
    if email != '':
        records = selectFromDB(table_name='generated_files', 
                                field_names=['email', 'status'], 
                                field_values=[[email], valid_file_statuses],
                                order_by_field_names=['file_name'])
    else:
        records = selectFromDB(table_name='generated_files', 
                                field_names=['session', 'status'], 
                                field_values=[[session_id], valid_file_statuses],
                                order_by_field_names=['file_name'])
        
    
    if records.empty: return records

    records_vector_db_collections = selectFromDB(table_name='vector_db_collections',
                        field_names=['generated_files_id', 'status'],
                        field_values=[list(map(int, records['id'].unique())), [vector_db_collections_status.ACTIVE.value]])

    records_settings = selectFromDB(table_name='settings',
                        field_names=['id'],
                        field_values=[list(map(int, records['settings_id'].unique()))])
    
    records = pd.merge(left=records, 
                        right=records_vector_db_collections[['id', 'generated_files_id', 'type']], 
                        left_on='id', right_on='generated_files_id', how='left',
                        suffixes=[None, '_vector_db_collections'])
    
    records = pd.merge(left=records, 
                        right=records_settings[['id', 'llm', 'temperature', 'instructions']], 
                        left_on='settings_id', right_on='id', how='left',
                        suffixes=[None, '_settings'])
    
    records_pivot = {}
    cols = list(records.columns[~records.columns.isin(['type', 'id_vector_db_collections', '_sa_instance_state'])])
    for i, row in records.iterrows():
        key = tuple(row[cols])
        records_pivot[key] = records_pivot.get(key, [None, None])
        if not pd.isna(row['id_vector_db_collections']):
            if row['type'] == 'uploaded_files':
                records_pivot[key][0] = row['id_vector_db_collections']
            elif row['type'] == 'literature':
                records_pivot[key][1] = row['id_vector_db_collections']
    
    records_pivot = pd.DataFrame([list(k) + v for k, v in records_pivot.items()], columns = cols + ['vector_db_collections_id_uploaded_files', 'vector_db_collections_id_literature'])

    records_pivot = records_pivot.replace({float('nan'): None})

    return records_pivot


@print_func_name
def getDocContent(file_id, attached_files=[], file_info={}):

    @print_func_name
    def processCitation(content):

        # d_files = {str(k): v for k, v, _ in attached_files}
        # used_files_info = {}

        # refs = re.findall(r'\[CITE\((\d+?)\)\]', content)

        # d_ref = {}
        # ref_list = []
        # for ref in refs:
        #     if ref not in d_files: continue
        #     try:
        #         d_ref[ref] = ref_list.index(d_files[ref]) + 1
        #     except ValueError:
        #         ref_list.append(d_files[ref])
        #         d_ref[ref] = len(ref_list)
        
        # for ref, ref_index in d_ref.items():
        #     content = content.replace(f'CITE({ref})', f'{ref_index}')
        #     used_files_info[ref] = file_info[ref] 

        # return content, used_files_info
    
        attached_references = {str(k): v for k, v, _ in attached_files}
        
        ref_groups = re.findall(r'\[CITE\((.+?(,\ ?.+?)*)\)\]', content)
    
        refs_seen = set()
        d_ref = {}
        ref_list = []
        used_files_info = {}
        for refs, _ in ref_groups:
            if refs in refs_seen: continue
            refs_seen.add(refs)
            for ref in refs.split(','):
                ref = ref.strip()
                if ref not in attached_references: continue
                if ref in d_ref: continue
                try:
                    d_ref[ref] = ref_list.index(attached_references[ref]) + 1
                except ValueError:
                    ref_list.append(attached_references[ref])
                    d_ref[ref] = len(ref_list)
                    used_files_info[ref] = file_info[ref]
        
            ref_links = sorted([str(d_ref[ref.strip()]) for ref in refs.split(',') if ref in d_ref])
            content = content.replace(f'[CITE({refs})]', f'[{', '.join(ref_links)}]')
    
        return content, used_files_info
    
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

    @print_func_name
    def extractContentFromOutline(d, raw_outline=[], counter=1):

        if not isinstance(d, dict):
            for k, v in d:
                raw_outline.append(v)
        else:
            for k in d:
                raw_outline = extractContentFromOutline(d[k], raw_outline + [f'{'#' * counter} {k}'] if k != 'content' else raw_outline, counter+1)

        return raw_outline

    outline_file_path = Config.DIR_DATA / f'outline_{file_id}.json'

    with open(outline_file_path) as fp:
        d_outline = json.load(fp)

    content = '\n'.join(extractContentFromOutline(d_outline))
    if attached_files: 
        content, used_files_info = processCitation(content)
        bibs = getBibFormat(used_files_info)
    else:
        bibs = ''

    return content, bibs
    