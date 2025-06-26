from shiny.express import render, module
from shiny.types import ImgData
from utils import Config
from pathlib import Path
from .db import selectFromDB, updateDB, \
                vector_db_collections_status, \
                generated_files_status, \
                generated_files_ai_architecture
from ..backend.vectordb import deleteCollection
from datetime import datetime

def getFileType(file_name):

    if Path(file_name).suffix not in ['.docx', '.pdf']:
        return 'txt'
    return Path(file_name).suffix[1:]

@module
def getFileTypeIcon(input, output, session, file_type):
    
    @render.image()
    def icon():
        img: ImgData = {"src": str(Config.DIR_HOME / 'assets' / f'{file_type}_icon.png'), 
                        "width": "100%"}
        return img
    
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

def detachDocs(generated_files_id, vector_db_collections_id):

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

    vector_db_collection_name = f'{Config.APP_NAME.lower().replace(' ', '_')}_collection_{vector_db_collections_id}'
    deleteCollection(vector_db_collection_name)

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
        
    return records