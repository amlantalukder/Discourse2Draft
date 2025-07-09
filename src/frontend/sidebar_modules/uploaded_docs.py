from shiny import reactive
from shiny.express import ui, module, render, expressify
from shiny.types import FileInfo
import faicons
from ..common import getFileType, getFileTypeIcon
from ...backend.db import selectFromDB, insertIntoDB, updateDB, \
                uploaded_files_status, \
                vector_db_collections_status, \
                generated_files_status, \
                generated_files_ai_architecture
from ...backend.ai.architecture import Architecture
from ...backend.vectordb import getLoader, ChromaDB
from pathlib import Path
from datetime import datetime
from utils import Config, print_func_name

selected_docs = set()

@module
def getUploadedDocItemView(input, output, session, doc, is_selected, changeSelectedDocs, select_all_docs, reload_parent_view_flag, showGeneratedDocsDetailedView):

    with ui.hold() as content:
        with ui.div(class_='d-flex gap-3'):
            with ui.div(class_='col-auto d-flex align-items-center'):
                ui.input_checkbox(id='chk_file', label='', value=is_selected)
            with ui.div(class_='col'):
                with ui.div(class_='uploaded-file-info-container'):
                    with ui.div(class_='col-2 d-flex align-items-center'):
                        getFileTypeIcon('icon', file_type=getFileType(doc['file_name']))
                    with ui.div(class_='col d-flex flex-column'):
                        with ui.tooltip():
                            ui.span(doc['file_name'], class_='cut-text')
                            doc['file_name']
                        ui.span(doc['update_date'].strftime('%Y-%m-%d %H:%M:%S'), class_='date')
            with ui.div(class_='col-auto d-flex align-items-center'):
                ui.input_action_button(f'btn_delete', '', icon=faicons.icon_svg('trash'))

    @reactive.effect
    @reactive.event(input.chk_file, ignore_init=True)
    @print_func_name
    def addOrRemoveDoc():
        changeSelectedDocs(doc['id'], doc['file_name'], input.chk_file())

    @reactive.effect
    @reactive.event(select_all_docs, ignore_init=True)
    @print_func_name
    def addOrRemoveDocSelectAll():
        ui.update_checkbox(id='chk_file', value=select_all_docs.get())

    @reactive.effect
    @reactive.event(input.btn_show_detailed_generated_docs)
    @print_func_name
    def showGeneratedDocs():
        showGeneratedDocsDetailedView()

    @print_func_name
    def showDeleteFileConfirmationDialog(generated_file_name_list):

        @print_func_name
        @expressify
        def renderView():
            with ui.div():

                ui.span("This document is being used by the following files.") 

                @render.express
                @print_func_name
                def renderGeneratedFilesUsingUploadedFile():
                    for file_name in generated_file_name_list:
                        with ui.div(class_='d-flex ms-2 gap-2'):
                            ui.span(faicons.icon_svg("hand-point-right", "regular"))
                            file_name

                ui.span("To remove the document, please", class_='me-1')
                ui.input_action_link(id='btn_show_detailed_generated_docs', label="de-attach this document", class_='me-1')
                ui.span("from these files.")

        with ui.hold() as content:
            renderView()

        ui.notification_show(content, type='message', duration=10)

    @print_func_name
    def checkIfDocIsUnderUse() -> list:

        records = selectFromDB(table_name='vector_db_collection_files',
                     field_names=['uploaded_files_id'],
                     field_values=[[doc['id']]])
        
        if records.empty: return []

        records = selectFromDB(table_name='vector_db_collections',
                                field_names=['id', 'status'],
                                field_values=[list(map(int, records['vector_db_collections_id'].unique())), [vector_db_collections_status.ACTIVE.value]])
            
        if records.empty: return []

        valid_file_statuses = list({e.value for e in generated_files_status} - {generated_files_status.DELETED.value})

        records = selectFromDB(table_name='generated_files',
                                field_names=['vector_db_collections_id', 'status'],
                                field_values=[list(map(int, records['id'].unique())), valid_file_statuses])
        
        if records.empty: return []
        
        return list(records['file_name'].values)
            

    @reactive.effect
    @reactive.event(input.btn_delete, ignore_init=True)
    @print_func_name
    def showDeleteFileConfirmation():
        
        files_that_use_this_doc = checkIfDocIsUnderUse()

        if files_that_use_this_doc:
            showDeleteFileConfirmationDialog(files_that_use_this_doc)
        else:
            deleteFile()

    @print_func_name
    def deleteFile():
        updateDB(table_name='uploaded_files', 
                update_fields=['status', 'update_date'], 
                update_values=[uploaded_files_status.DELETED.value, datetime.now()], 
                select_fields=['id'], 
                select_values=[[doc['id']]])
        
        reload_parent_view_flag.set(not reload_parent_view_flag.get())

    return content


@module
def mod_uploaded_docs_view(input, output, session, config_app, reload_rag_and_ref_flag, showGeneratedDocsDetailedView):

    reload_view_flag = reactive.value(True)
    selected_docs_changed_flag = reactive.value(True)
    select_all_docs = reactive.value(False)

    ui.input_file("btn_upload_docs", "Choose Documents", accept=[".txt", ".csv", ".docx", ".pdf"], multiple=True)

    with ui.div(class_='side-bar-docs-container'):
        
        @render.express
        @print_func_name
        def renderUploadedDocs():

            docs = getUploadedDocs()

            if docs.empty:
                ui.span('No uploaded documents')
                return

            with ui.div(class_='d-flex gap-3'):
                with ui.div(class_='col-auto d-flex align-items-center'):
                    ui.input_checkbox(id='chk_all_uploaded_files', label='', value=False)
                with ui.div(class_='col d-flex align-items-center'):
                    ui.strong('Select all documents')

            docs['is_selected'] = [(row['id'], row['file_name']) in selected_docs for _, row in docs.iterrows()]

            with ui.div(class_='doc-container'):
                with ui.div(class_='d-flex flex-column gap-3'):
                    for i, row in docs.iterrows():
                        getUploadedDocItemView(id=str(i), 
                                            doc=row, 
                                            is_selected=row['is_selected'],
                                            changeSelectedDocs=changeSelectedDocs, 
                                            select_all_docs=select_all_docs,
                                            reload_parent_view_flag=reload_view_flag,
                                            showGeneratedDocsDetailedView = showGeneratedDocsDetailedView)

    @render.express
    @print_func_name
    def showAttachButton():

        if getSelectedDocs():
            with ui.div(class_='text-center mt-2'):
                ui.input_action_button(id='btn_attach_docs', label='Attach docs')

    @reactive.calc
    @reactive.event(selected_docs_changed_flag)
    @print_func_name
    def getSelectedDocs():
        return selected_docs

    @reactive.effect
    @reactive.event(input.btn_upload_docs)
    @print_func_name
    def uploadedDocs():

        files: list[FileInfo] | None = input.btn_upload_docs()
        
        if files is None: return

        for file in files:

            current_time = datetime.now()
            
            if config_app.email != '':
                records = selectFromDB(table_name='uploaded_files', 
                                field_names=['email', 'file_name', 'status'],
                                field_values=[[config_app.email], [file['name']], [uploaded_files_status.UPLOADED.value]])
            else:
                records = selectFromDB(table_name='uploaded_files', 
                                field_names=['session', 'file_name', 'status'],
                                field_values=[[config_app.session_id], [file['name']], [uploaded_files_status.UPLOADED.value]])
            
            if records.empty:

                ids = insertIntoDB(table_name='uploaded_files', 
                            field_names=['email', 'session', 'file_name', 'status', 'update_date'], 
                            field_values=[[config_app.email], [config_app.session_id], [file['name']], [uploaded_files_status.UPLOADED.value], [current_time]])
                uploaded_file_id = ids[0]
                
            else:
                updateDB(table_name='uploaded_files', 
                        update_fields=['status', 'update_date'], 
                        update_values=[uploaded_files_status.UPLOADED.value, current_time], 
                        select_fields=['id'], 
                        select_values=[list(map(int, records.id.values))])
                uploaded_file_id = records.iloc[0].id
                
            with open(Config.DIR_DATA / 'uploaded_docs' / f'{uploaded_file_id}{Path(file['datapath']).suffix}', 'wb') as fp:
                with open(file['datapath'], 'rb') as fp_r:
                    fp.write(fp_r.read())

        reload_view_flag.set(not reload_view_flag.get())

    @reactive.calc
    @reactive.event(reload_view_flag)
    @print_func_name
    def getUploadedDocs():

        if config_app.email != '':
            docs = selectFromDB(table_name='uploaded_files', 
                            field_names=['email', 'status'],
                            field_values=[[config_app.email], [uploaded_files_status.UPLOADED.value]],
                            order_by_field_names=['file_name'])
        else:
            docs = selectFromDB(table_name='uploaded_files', 
                            field_names=['session', 'status'],
                            field_values=[[config_app.session_id], [uploaded_files_status.UPLOADED.value]],
                            order_by_field_names=['file_name'])

        return docs
    
    @reactive.effect
    @reactive.event(input.chk_all_uploaded_files, ignore_init=True)
    @print_func_name
    def selectAllUploadedDocs():
        select_all_docs.set(input.chk_all_uploaded_files())

    @print_func_name
    def changeSelectedDocs(file_id, file_name, is_selected):
        global selected_docs
        if is_selected:
            selected_docs |= {(file_id, file_name)}
        else:
            selected_docs -= {(file_id, file_name)}

        selected_docs_changed_flag.set(not selected_docs_changed_flag.get())

    @print_func_name
    def createVectorDBCollection(collection_name: str, file_paths: list[Path], progress=None):
    
        docs = []

        progress_counter = 1

        for file_path in file_paths:
            
            if progress is not None:
                progress.set(progress_counter, f'Extracting file {progress_counter}')
                progress_counter += 1
            
            loader = getLoader(file_path=file_path)
            
            for doc in loader:
                doc.metadata = {**{'app_file_id': Path(file_path).stem}, **{k: str(v) for k, v in doc.metadata.items()}}
                docs.append(doc)

        if progress is not None:
            progress.set(progress_counter, 'Creating vector db')

        db = ChromaDB()
        db.create(collection_name=collection_name, delete_if_exists=True)
        db.add(docs=docs)

    @reactive.effect
    @reactive.event(input.btn_attach_docs)
    @print_func_name
    def attachDocs():
        
        if not selected_docs:
            ui.notification_show("Please select a document to attach.", type="error")
            return
        
        if not config_app.generated_files_id:
            ui.notification_show("Please create a new file or select an existing file.", type="error")
            return

        current_time = datetime.now()

        if config_app.vector_db_collections_id:

            updateDB(table_name='vector_db_collections', 
                update_fields=['status', 'update_date'], 
                update_values=[vector_db_collections_status.DELETED.value, current_time], 
                select_fields=['id'], 
                select_values=[[config_app.vector_db_collections_id]])

        ids = insertIntoDB(table_name='vector_db_collections', 
                    field_names=['email', 'session', 'status', 'create_date', 'update_date'],
                    field_values=[[config_app.email], [config_app.session_id], ['active'], [current_time], [current_time]]) 

        insertIntoDB(table_name='vector_db_collection_files', 
                    field_names=['vector_db_collections_id', 'uploaded_files_id', 'create_date', 'update_date'],
                    field_values=[ids * len(selected_docs), 
                                sorted([file_id for file_id, _ in selected_docs]), 
                                [current_time] * len(selected_docs), 
                                [current_time] * len(selected_docs)])
        
        file_paths = [Config.DIR_DATA / 'uploaded_docs' / f'{file_id}{Path(file_name).suffix}' for file_id, file_name in selected_docs]
        with ui.Progress(min=1, max=len(file_paths)+1) as p:

            p.set(message="Processing", detail="This may take a while...")
        
            vector_db_collection_name = f'{Config.APP_NAME.lower().replace(' ', '_')}_collection_{int(ids[0])}'
            createVectorDBCollection(collection_name=vector_db_collection_name, file_paths=file_paths, progress=p)
        
        ai_architecture = generated_files_ai_architecture.RAG.value

        updateDB(table_name='generated_files', 
                update_fields=['ai_architecture', 'vector_db_collections_id', 'update_date'], 
                update_values=[ai_architecture, ids[0], current_time], 
                select_fields=['id'], 
                select_values=[[config_app.generated_files_id]])

        config_app.vector_db_collections_id = ids[0]
        config_app.agent = Architecture(model_name=config_app.llm, 
                                        temperature=config_app.temperature, 
                                        instructions=config_app.instructions, 
                                        type=ai_architecture, 
                                        collection_name=vector_db_collection_name).agent

        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())