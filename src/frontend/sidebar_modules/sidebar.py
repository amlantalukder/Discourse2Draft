from shiny import reactive
from shiny.express import ui, render, module, expressify
from shiny.types import FileInfo
import faicons
from .generated_docs import getGeneratedDocItemView, mod_generated_doc_detailed_view
from .uploaded_docs import getUploadedDocItemView
from ..db import selectFromDB, insertIntoDB, updateDB, \
                uploaded_files_status, \
                generated_files_ai_architecture, \
                vector_db_collections_status
from ...backend.vectordb import getLoader, ChromaDB
from ...backend.architecture import Architecture
from ..common import getGeneratedDocuments
from utils import Config
from pathlib import Path
from datetime import datetime
import uuid

@module
def mod_sidebar(input, output, session, config_app, reload_rag_and_ref_flag, setCurrentFile, reload_sidebar_view_flag):

    selected_docs_changed_flag = reactive.value(True)
    select_all_docs = reactive.value(False)

    with ui.hold() as content:
        with ui.div():
            with ui.accordion(id='acc_sidebar', open='Generated Documents' if config_app.email != '' else '', multiple=False):
                with ui.accordion_panel('Generated Documents'):

                    with ui.div(class_='side-bar-docs-container'):
                        
                        @render.express
                        def showGeneratedDocuments():

                            print('showGeneratedDocuments')

                            records = applyGetGeneratedDocuments()
                        
                            if records.empty: 
                                ui.span('No generated documents')
                                return
                            
                            with ui.div(class_='d-flex justify-content-end'):
                                with ui.div(class_='d-flex', style='width:20px'):
                                    ui.input_action_link(id='btn_show_generated_docs_details', 
                                                        label='',
                                                        icon=faicons.icon_svg('maximize'))
                            with ui.div(class_='doc-container'):
                                with ui.div(class_='d-flex flex-column gap-3'):
                                    for i, row in records.iterrows():
                                        getGeneratedDocItemView(f'doc_list_item_{str(uuid.uuid4()).replace('-', '_')}_{i}', 
                                                        info=row,
                                                        show_expanded_view=False,
                                                        setCurrentFile=setCurrentFile, 
                                                        reload_parent_view_flag=reload_sidebar_view_flag)
                            
                with ui.accordion_panel('Uploaded Documents'):
                    ui.input_file("btn_upload_docs", "Choose Documents", accept=[".txt", ".csv", ".docx", ".pdf"], multiple=True)

                    with ui.div(class_='side-bar-docs-container'):
                        
                        @render.express
                        def _():

                            docs = getUploadedDocs()

                            if docs.empty:
                                ui.span('No uploaded documents')
                                return

                            with ui.div(class_='d-flex gap-3'):
                                with ui.div(class_='col-auto d-flex align-items-center'):
                                    ui.input_checkbox(id='chk_all_uploaded_files', label='', value=False)
                                with ui.div(class_='col d-flex align-items-center'):
                                    ui.strong('Select all documents')

                            docs['is_selected'] = [(row['id'], row['file_name']) in config_app.selected_docs for _, row in docs.iterrows()]

                            with ui.div(class_='doc-container'):
                                with ui.div(class_='d-flex flex-column gap-3'):
                                    for i, row in docs.iterrows():
                                        getUploadedDocItemView(id=str(i), 
                                                            doc=row, 
                                                            is_selected=row['is_selected'],
                                                            changeSelectedDocs=changeSelectedDocs, 
                                                            select_all_docs=select_all_docs,
                                                            reload_sidebar_view_flag=reload_sidebar_view_flag,
                                                            showDetailedGeneratedDocs = showDetailedGeneratedDocs)

                    @render.express
                    def showAttachButton():
                
                        if getSelectedDocs():
                            with ui.div(class_='text-center mt-2'):
                                ui.input_action_button(id='btn_attach_docs', label='Attach docs')

    @reactive.effect
    def loadViews():
        global generated_doc_detailed_view
        generated_doc_detailed_view = mod_generated_doc_detailed_view(id='generated_doc_detailed', 
                                              config_app=config_app, 
                                              setCurrentFile=setCurrentFile)
        
    @reactive.calc()
    @reactive.event(reload_sidebar_view_flag)
    def applyGetGeneratedDocuments():

        return getGeneratedDocuments(email=config_app.email, session_id=config_app.session_id)
    
    def showDetailedGeneratedDocs():

        m = ui.modal(
            generated_doc_detailed_view,
            title="Generated documents",
            easy_close=True,
            footer=None,
            size='xl'
        )

        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.btn_show_generated_docs_details)
    def openDetailedGeneratedDocsView():

        showDetailedGeneratedDocs()

    @reactive.calc
    @reactive.event(selected_docs_changed_flag)
    def getSelectedDocs():
        return config_app.selected_docs

    @reactive.effect
    @reactive.event(input.btn_upload_docs)
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

        reload_sidebar_view_flag.set(not reload_sidebar_view_flag.get())

    @reactive.calc
    @reactive.event(reload_sidebar_view_flag)
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
    def selectAllUploadedDocs():
        print('all uploaded files')

        select_all_docs.set(input.chk_all_uploaded_files())

    def changeSelectedDocs(file_id, file_name, is_selected):
        if is_selected:
            config_app.selected_docs |= {(file_id, file_name)}
        else:
            config_app.selected_docs -= {(file_id, file_name)}

        selected_docs_changed_flag.set(not selected_docs_changed_flag.get())

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
    def attachDocs():
        
        if not config_app.selected_docs:
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
                    field_values=[ids * len(config_app.selected_docs), 
                                sorted([file_id for file_id, _ in config_app.selected_docs]), 
                                [current_time] * len(config_app.selected_docs), 
                                [current_time] * len(config_app.selected_docs)])
        
        file_paths = [Config.DIR_DATA / 'uploaded_docs' / f'{file_id}{Path(file_name).suffix}' for file_id, file_name in config_app.selected_docs]
        with ui.Progress(min=1, max=len(file_paths)+1) as p:

            p.set(message="Processing", detail="This may take a while...")
        
            vector_db_collection_name = f'{Config.APP_NAME.lower().replace(' ', '_')}_collection_{ids[0]}'
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

    return content