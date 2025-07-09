from shiny.express import render, module
from shiny.types import ImgData
from utils import Config, print_func_name
from pathlib import Path
import pandas as pd
from ..backend.db import selectFromDB, updateDB, \
                vector_db_collections_status, \
                generated_files_status, \
                generated_files_ai_architecture
from ..backend.vectordb import deleteCollection
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
        img: ImgData = {"src": str(Config.DIR_HOME / 'assets' / f'{file_type}_icon.png'), 
                        "width": "100%"}
        return img
    
@print_func_name
def getVectorDBFiles(vector_db_collections_id):

    if vector_db_collections_id is None: return []

    vector_db_collection_records = selectFromDB(table_name='vector_db_collections', 
                                                field_names=['id', 'status'], 
                                                field_values=[[int(vector_db_collections_id)], [vector_db_collections_status.ACTIVE.value]])
    
    if vector_db_collection_records.empty: return []
    
    vector_db_collection_files_records = selectFromDB(table_name='vector_db_collection_files', 
                                                field_names=['vector_db_collections_id'], 
                                                field_values=[[int(vector_db_collections_id)]])
    
    uploaded_files_records = selectFromDB(table_name='uploaded_files',
                                            field_names=['id'],
                                            field_values=[list(map(int, vector_db_collection_files_records['uploaded_files_id'].values))])
    
    return list(uploaded_files_records[['id', 'file_name']].values)

@print_func_name
def detachDocs(generated_files_id, vector_db_collections_id):

    if vector_db_collections_id is None: return

    current_time = datetime.now()

    updateDB(table_name='generated_files', 
            update_fields=['ai_architecture', 'vector_db_collections_id', 'update_date'], 
            update_values=[generated_files_ai_architecture.BASE.value, None, current_time], 
            select_fields=['id'], 
            select_values=[[generated_files_id]])
    
    updateDB(table_name='vector_db_collections', 
                update_fields=['status', 'update_date'],
                update_values=[vector_db_collections_status.DELETED.value, current_time],
                select_fields=['id'], 
                select_values=[[vector_db_collections_id]]) 

    vector_db_collection_name = f'{Config.APP_NAME.lower().replace(' ', '_')}_collection_{int(vector_db_collections_id)}'
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

    records_settings = selectFromDB(table_name='settings',
                        field_names=['id'],
                        field_values=[list(map(int, records['settings_id'].unique()))])
    records = pd.merge(left=records, 
                        right=records_settings[['id', 'llm', 'temperature', 'instructions']], 
                        left_on='settings_id', right_on='id', how='left',
                        suffixes=[None, '_settings'])
    return records


@print_func_name
def getDocContent(file_id, attached_files=[]):

    @print_func_name
    def processCitation(content):

        d_files = {str(k): v for k, v in attached_files}

        refs = re.findall(r'\[CITE\((\d+?)\)\]', content)

        d_ref = {}
        ref_list = []
        for ref in refs:
            if ref not in d_files: continue
            try:
                d_ref[ref] = ref_list.index(d_files[ref]) + 1
            except ValueError:
                ref_list.append(d_files[ref])
                d_ref[ref] = len(ref_list)
        
        for ref, ref_index in d_ref.items():
            content = content.replace(f'CITE({ref})', f'{ref_index}')

        return content

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
    if attached_files: content = processCitation(content)

    return content
    