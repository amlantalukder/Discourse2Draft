from shiny import reactive, ui as core_ui
from shiny.express import ui, render, module, expressify
from shiny.types import FileInfo, ImgData
import faicons
from utils import Config, read_in_chunks
from .db import updateDB, selectFromDB, insertIntoDB, \
            generated_files_ai_architecture, \
            generated_files_status, \
            uploaded_files_status, \
            vector_db_collections_status
from src.backend.vectordb import getLoader, ChromaDB, deleteCollection
import asyncio
import json
import textwrap
from datetime import datetime
from pathlib import Path

def getFileType(file_name):

    if Path(file_name).suffix not in ['.docx', '.pdf']:
        return 'txt'
    return Path(file_name).suffix[1:]

@module
def getFileTypeIcon(input, output, session, file_type):
    
    @render.image()
    def icon():
        img: ImgData = {"src": str(Config.DIR_HOME / 'assets' / f'{file_type}_icon.png'), 
                        "width": "30px"}
        return img

@module
def mod_main(input, output, session, config_app, updateFileNameFlag, reload_flag):
    
    file_change_flag = reactive.value(True)
    show_outline = reactive.value(True)
    reload_flag_sidebar = reactive.value(True)
    selected_docs_changed_flag = reactive.value(True)
    reload_rag_and_ref_flag = reactive.value(True)
    select_all_docs = reactive.value(False)

    stream = ui.MarkdownStream("stream")

    @module
    def getSavedDocItemView(input, output, session, info, show_expanded_view):

        @reactive.effect
        @reactive.event(input.btn_show, ignore_init=True)
        def showFile():
            setCurrentFile(info['id'], info['file_name'], info['vector_db_collections_id'])

        @reactive.effect
        @reactive.event(input.btn_delete, ignore_init=True)
        def deleteFile():
            updateDB('generated_files', 
                    update_fields=['status', 'update_date'], 
                    update_values=[generated_files_status.DELETED.value, datetime.now()], 
                    select_fields=['id'], 
                    select_values=[[info['id']]])
            reload_flag_sidebar.set(not reload_flag_sidebar.get())
        
        with ui.hold() as content:
            if not show_expanded_view:
                with ui.div(class_='d-flex gap-3'):
                    with ui.div(class_='col d-flex flex-column justify-content-center'):
                        with ui.tooltip():
                            ui.input_action_link('btn_show', info['file_name'], class_='cut-text')
                            info['file_name']                       
                        ui.span(info['update_date'].strftime('%Y-%m-%d %H:%M:%S'), class_='date')
                    with ui.div(class_='col-auto d-flex align-items-center'):
                        @render.download(label=faicons.icon_svg("download"), filename='manuscript.md')
                        async def downloadDoc():
                            doc_path = Config.DIR_DATA / f'manuscript_{info['id']}.md'

                            if not doc_path.exists(): return
                            with open(doc_path) as f:
                                for l in f.readlines():
                                    yield l
                    with ui.div(class_='col-auto d-flex align-items-center'):
                        ui.input_action_button(f'btn_delete', '', icon=faicons.icon_svg('trash'))
            else:
                with ui.div(class_='app-tr row'):
                    with ui.div(class_='app-td col'):
                        ui.input_action_link('btn_show', info["file_name"])
                    with ui.div(class_='app-td col-2'):
                        ui.span(config_app.generated_files_status_desc[info['status']])
                    with ui.div(class_='app-td col-2'):
                        ui.span(info['create_date'].strftime('%Y-%m-%d %H:%M:%S'))
                    with ui.div(class_='app-td col-2'):
                        ui.span(info['update_date'].strftime('%Y-%m-%d %H:%M:%S'))
                    with ui.div(class_='app-td col-1 justify-content-center'):
                        with ui.div():
                            @render.download(label=faicons.icon_svg("download"), filename='manuscript.md')
                            async def downloadDoc():
                                doc_path = Config.DIR_DATA / f'manuscript_{info['id']}.md'

                                if not doc_path.exists(): return
                                with open(doc_path) as f:
                                    for l in f.readlines():
                                        yield l
                    with ui.div(class_='app-td col-1 justify-content-center'):
                        with ui.div():
                            ui.input_action_button(f'btn_delete', '', icon=faicons.icon_svg('trash'))

        return content
    
    @module
    def getUploadedDocItemView(input, output, session, doc, is_selected):

        @reactive.effect
        @reactive.event(input.chk_file, ignore_init=True)
        def addOrRemoveDoc():
            print('add or remove doc')
            print((doc['id'], doc['file_name']), input.chk_file())
            changeSelectedDocs(doc['id'], doc['file_name'], input.chk_file())

        @reactive.effect
        @reactive.event(select_all_docs, ignore_init=True)
        def addOrRemoveDocSelectAll():
            print('add or remove doc all')
            ui.update_checkbox(id='chk_file', value=select_all_docs.get())
        
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

        return content

    with ui.hold() as content:
        with ui.div(class_='app-body-container'):
            with ui.card(id='ctx_menu', style='display: none; position: absolute; z-index: 10; width: 250px; height: 75px'):
                ui.input_action_button(id='btn_regenerate_text', label='Regenerate paragraph')
            with ui.layout_sidebar():
                with ui.sidebar(id='sidebar_docs', position="left", open='closed' if config_app.email == '' else 'open', bg="#f8f8f8", width=400):
                    with ui.div():
                        with ui.accordion(id='acc_sidebar', open='Generated Documents' if config_app.email != '' else '', multiple=False):
                            with ui.accordion_panel('Generated Documents'):
                                
                                with ui.div(class_='side-bar-docs-container'):
                                    @render.express
                                    def showSavedDocuments():
                                        records = loadDocuments()
                                    
                                        if records.empty: 
                                            ui.span('No documents')
                                            return
                                        
                                        with ui.div(class_='d-flex justify-content-end'):
                                            with ui.div(class_='d-flex', style='width:20px'):
                                                ui.input_action_link(id='btn_show_saved_docs_details', 
                                                                    label='',
                                                                    icon=faicons.icon_svg('maximize'))
                                        with ui.div(class_='doc-container'):
                                            with ui.div(class_='d-flex flex-column gap-3'):
                                                for i, row in records.iterrows():
                                                    getSavedDocItemView(f'doc_list_item_{i}', 
                                                                    info=row,
                                                                    show_expanded_view=False)
                                        
                            with ui.accordion_panel('Uploaded Documents'):
                                ui.input_file("btn_upload_docs", "Choose Documents", accept=[".txt", ".csv", ".docx", ".pdf"], multiple=True)

                                with ui.div(class_='side-bar-docs-container'):
                                    
                                    @render.express
                                    def _():
                                        with ui.div(class_='d-flex gap-3'):
                                            with ui.div(class_='col-auto d-flex align-items-center'):
                                                ui.input_checkbox(id='chk_all_uploaded_files', label='', value=False)
                                            with ui.div(class_='col d-flex align-items-center'):
                                                ui.strong('Select all documents')
                                    
                                    @render.express
                                    def showUploadedDocuments():

                                        print('show uploaded docs')
                                        
                                        docs = getUploadedDocs()
                                        if docs.empty: return

                                        docs['is_selected'] = [(row['id'], row['file_name']) in config_app.selected_docs for _, row in docs.iterrows()]

                                        with ui.div(class_='doc-container'):
                                            with ui.div(class_='d-flex flex-column gap-3'):
                                                for i, row in docs.iterrows():
                                                    getUploadedDocItemView(id=str(i), doc=row, is_selected=row['is_selected'])

                                @render.express
                                def showAttachButton():
                                    print('show uploaded docs attach')
                                    if getSelectedDocs():
                                        with ui.div(class_='text-center mt-2'):
                                            ui.input_action_button(id='btn_attach_docs', label='Attach docs')

                with ui.div(class_='app-body'):
                    with ui.div(class_='row input'):
                        @render.express
                        def showOutline():
                            class_name_outline, class_name_controls = ('col', 'row flex-column gap-2') if show_outline.get() else ('col d-none', 'row flex-row gap-2')
                            with ui.div(class_=class_name_outline):
                                with ui.div(class_='row justify-content-between', style='font-size: 0.8em !important'):
                                    with ui.div(class_='col-4'):
                                        ui.input_checkbox('chk_example', 'Use example', value=False)
                                    with ui.div(class_='d-flex flex-column col-4 text-center'):
                                        @render.ui
                                        def showLLMandTemp():
                                            if reload_flag() in [True, False]:
                                                return [ui.span(f'LLM: {config_app.llm}, Temperature: {config_app.temperature}'),
                                                        ui.span('(Can be changed in the settings panel in the top-right corner)')]
                                    with ui.div(class_='col-4 text-end'):
                                        ui.p("(Drag the text area from the bottom right corner to show more text)")
                                ui.input_text_area(id='text_outline', label='', placeholder='''Write an outline...''', rows=8, width='100%')
                            with ui.div(class_='col-auto d-flex justify-content-around align-items-end p-3'):
                                with ui.div(class_=class_name_controls):
                                    @render.express
                                    def showOutlineControl():
                                        text, ico = ('Hide outline', 'eye-slash') if show_outline.get() else ('Show outline', 'eye')
                                        with ui.tooltip(placement="right"):
                                            ui.input_action_button('btn_show_hide_outline', '', icon=faicons.icon_svg(ico))
                                            text 
                                    with ui.tooltip(placement="right"):
                                        ui.input_action_button('btn_regenerate', '', icon=faicons.icon_svg("repeat"))
                                        "Write from the start"
                                    with ui.tooltip(placement="right"):
                                        ui.input_action_button('btn_resume_pause', '', icon=faicons.icon_svg("play"))
                                        "Resume / Pause"
                                    with ui.tooltip(placement="right"):
                                        ui.input_action_button('btn_speed', '', icon=faicons.icon_svg("person-running"))
                                        "Writing Speed"
                                    with ui.tooltip(placement="right"):
                                        @render.download(label=faicons.icon_svg("download"), filename='manuscript.md')
                                        async def downloadDoc():

                                            doc_path = Config.DIR_DATA / f'manuscript_{config_app.generated_files_id}.md'

                                            if not doc_path.exists(): return
                                            with open(doc_path) as f:
                                                for l in f.readlines():
                                                    yield l
                                        "Download"
                                
                    with ui.div(class_='content-container'):
                        with ui.div(class_='content-header'):
                            ui.span('Content starts below ...')

                            @render.express
                            def showRAGAndRefInfo():
                                file_names = getVectorDBFiles()
                                
                                if not file_names: return
                
                                with ui.popover(placement='bottom', options={'trigger': 'focus'}):
                                    ui.input_action_link('dummy', 'Using context from attached documents', class_='text-link')
                                    with ui.div(class_='d-flex flex-column gap-2'):
                                        with ui.div():
                                            for i, file_name in enumerate(file_names):
                                                with ui.div(class_='row'):
                                                    with ui.div(class_='col-2 d-flex align-items-center'):
                                                        getFileTypeIcon(f'icon_{i}', file_type=getFileType(file_name))
                                                    with ui.div(class_='col'):
                                                        with ui.tooltip():
                                                            ui.span(file_name, class_='cut-text')
                                                            file_name
                                        with ui.div(class_='text-end'):
                                            with ui.popover():
                                                with ui.div():
                                                    ui.input_action_button(f'btn_delete_rag', '', icon=faicons.icon_svg('trash'))
                                                "Remove documents"
                                        
                        
                        with ui.div(class_='content', id='content'):
                            stream.ui(width='100%')

        ui.include_js(Config.DIR_HOME / "www" / "js" / "addon.js")

    @reactive.calc
    @reactive.event(selected_docs_changed_flag)
    def getSelectedDocs():
        return config_app.selected_docs        

    @reactive.effect
    @reactive.event(input.btn_show_saved_docs_details)
    def showDetailedSavedDocsView():

        @expressify
        def showSavedDocuments():
            records = loadDocuments()
            if records.empty: return ui.span('No documents')
            with ui.div(class_='app-table-container'):
                with ui.div(class_='app-table'):
                    with ui.div(class_='app-thead'):
                        with ui.div(class_='app-tr row'):
                            with ui.div(class_='app-th col'):
                                ui.strong('Document')
                            with ui.div(class_='app-th col-2'):
                                ui.strong('Status')
                            with ui.div(class_='app-th col-2'):
                                ui.strong('Create date')
                            with ui.div(class_='app-th col-2'):
                                ui.strong('Update date')
                            with ui.div(class_='app-th col-1 justify-content-center'):
                                ""
                            with ui.div(class_='app-th col-1 justify-content-center'):
                                ""
                    with ui.div(class_='app-tbody'):
                        for i, row in records.iterrows():
                            getSavedDocItemView(f'doc_list_item_exp_view_{i}', info=row, show_expanded_view=True)

        with ui.hold() as content:
            showSavedDocuments()

        m = ui.modal(
            content,
            title="Saved documents",
            easy_close=True,
            footer=None,
            size='xl'
        )

        ui.modal_show(m)

    @reactive.calc
    def getUploadedDocs():
        files: list[FileInfo] | None = input.btn_upload_docs()
        if files is not None:

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
                doc.metadata = {k: str(v) for k, v in doc.metadata.items()}
                docs.append(doc)

        if progress is not None:
            progress.set(progress_counter, 'Creating vector db')

        db = ChromaDB(collection_name=collection_name, delete_if_exists=True)
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

        ids = insertIntoDB(table_name='vector_db_collections', 
                    field_names=['email', 'session', 'create_date', 'update_date'],
                    field_values=[[config_app.email], [config_app.session_id], [current_time], [current_time]]) 

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

        config_app.ai_architecture = ai_architecture
        config_app.vector_db_collections_id = ids[0]

        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())

    @reactive.calc
    @reactive.event(reload_rag_and_ref_flag)
    def getVectorDBFiles():
        
        if not config_app.vector_db_collections_id: return []
        vector_db_collection_files_records = selectFromDB(table_name='vector_db_collection_files', 
                                                  field_names=['vector_db_collections_id'], 
                                                  field_values=[[config_app.vector_db_collections_id]])
        
        uploaded_files_records = selectFromDB(table_name='uploaded_files',
                                              field_names=['id'],
                                              field_values=[list(map(int, vector_db_collection_files_records['uploaded_files_id'].values))])
        
        return list(uploaded_files_records['file_name'].values)
    
    @reactive.effect
    @reactive.event(input.btn_delete_rag)
    def detachDocs():

        current_time = datetime.now()

        updateDB(table_name='generated_files', 
                update_fields=['ai_architecture', 'vector_db_collections_id', 'update_date'], 
                update_values=[generated_files_ai_architecture.PRETRAINING.value, None, current_time], 
                select_fields=['id'], 
                select_values=[[config_app.generated_files_id]])
        
        updateDB(table_name='vector_db_collections', 
                 update_fields=['status', 'update_date'],
                 update_values=[vector_db_collections_status.DELETED.value, current_time],
                 select_fields=['id'], 
                 select_values=[[config_app.vector_db_collections_id]]) 

        vector_db_collection_name = f'{Config.APP_NAME.lower().replace(' ', '_')}_collection_{config_app.vector_db_collections_id}'
        deleteCollection(vector_db_collection_name)

        config_app.vector_db_collections_id = None

        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())

        
    @reactive.effect
    @reactive.event(input.btn_show_hide_outline)
    def showOrHideOutline():
        show_outline.set(not show_outline.get())

        if not config_app.file_name: return
        
        outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'

        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        raw_outline = '\n'.join(createRawOutline(d_outline))
        ui.update_text(id='text_outline', value=raw_outline)

    def resetContentPara(d_outline, section_list, paragraph_index):
        '''
        Resets specified paragraph for regeneration within a section hierarchy
        '''
        
        if len(section_list) == 1:

            assert 'content' in d_outline[section_list[0]], 'Hierarchy does not contain content'

            count_par = 0

            for i, (_, content) in enumerate(d_outline[section_list[0]]['content']):
                
                # Detect the specified paragraph 
                count_par += content.count('\n\n') + 1
                if paragraph_index < count_par:
                    break
            
            assert i < len(d_outline[section_list[0]]['content']), 'Intended paragraph was not found for regeneration'
        
            # Reset the specified paragraph in the outline
            pars = content.split('\n\n')
            index_current_par = len(pars)-(count_par - paragraph_index)
            previous_para_current_content, next_para_current_content = [], []
            if index_current_par > 0:
                previous_para_current_content = [[d_outline[section_list[0]]['content'][i][0], '\n\n'.join(pars[:index_current_par])]]
            if index_current_par < len(pars)-1:
                next_para_current_content = [[d_outline[section_list[0]]['content'][i][0], '\n\n'.join(pars[index_current_par+1:])]]

            d_outline[section_list[0]]['content'] = (d_outline[section_list[0]]['content'][:i]
                                                    + previous_para_current_content
                                                    + [['content_ai', '']]
                                                    + next_para_current_content
                                                    + d_outline[section_list[0]]['content'][i+1:])
        else:
            resetContentPara(d_outline[section_list[0]], section_list[1:], paragraph_index)

    @reactive.effect
    @reactive.event(input.btn_regenerate_text)
    def regenerateParagraph():

        hierarchy = input.selected_para_hierarchy()
        if not hierarchy: return
        
        outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'
        manuscript_file_path = Config.DIR_DATA / f'manuscript_{config_app.generated_files_id}.md'
        
        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)
        
        *section_list, paragraph_index = hierarchy
        resetContentPara(d_outline, section_list, paragraph_index)

        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, outline_file_path, manuscript_file_path, write_n_contents=1), clear=True))

    @reactive.effect
    @reactive.event(reload_flag)
    def initView():
        # Reset file name, outline and content
        ui.update_checkbox(id='chk_example', value=False)
        updateFileNameFlag(config_app.file_name)
        ui.update_text(id='text_outline', value='')
        setContent('<p>Content starts here ...</p>')

    def setContent(content):
        loop = asyncio.get_event_loop()
        loop.create_task(stream._send_content_message(content, "replace", []))

    @reactive.calc()
    @reactive.event(reload_flag, reload_flag_sidebar)
    def loadDocuments():

        print('loading sidebar')

        valid_file_statuses = {e.value for e in generated_files_status} - {generated_files_status.DELETED.value}
        if config_app.email != '':
            records = selectFromDB(table_name='generated_files', 
                                   field_names=['email', 'status'], 
                                   field_values=[[config_app.email], valid_file_statuses],
                                   order_by_field_names=['file_name'])
        else:
            records = selectFromDB(table_name='generated_files', 
                                   field_names=['session', 'status'], 
                                   field_values=[[config_app.session_id], valid_file_statuses],
                                   order_by_field_names=['file_name'])
        return records

    @reactive.effect
    @reactive.event(input.chk_example)
    def useExample():
        
        example = textwrap.dedent('''\
        # Title: Hypertensive Disorders of Pregnancy: A Comprehensive Review of Pathophysiology, Clinical Management, Long-Term Implications, and Future Directions
        ## I. Introduction
        <content>
        ### A. Historical Perspective and Evolution of Understanding
        <content>
        ### B. Definition and Significance of Hypertensive Disorders of Pregnancy (HDP)
        #### 1. Global Burden of Disease (Maternal and Perinatal Morbidity & Mortality)
        <content>
        #### 2. Economic Impact
        <content>
        ### C. Classification of HDP (Overview based on major international guidelines - e.g., ACOG, ISSHP, WHO)
        #### 1. Chronic Hypertension (Pre-existing)
        <content>
        #### 2. Gestational Hypertension
        <content>
        #### 3. Preeclampsia
        <content>''')
        
        if not input.chk_example(): example = ''

        ui.update_text_area('text_outline', value=example)

    def createRawOutline(d, raw_outline=[], counter=1):

        if not isinstance(d, dict):
            for k, v in d:
                if k == 'content_ai':
                    raw_outline.append('<content>')
                else:
                    raw_outline.append(v)
        else:
            for k in d:
                raw_outline = createRawOutline(d[k], raw_outline + [f'{'#' * counter} {k}'] if k != 'content' else raw_outline, counter+1)

        return raw_outline
        

    def setCurrentFile(id, file_name, vector_db_collections_id=None):

        config_app.generated_files_id = id
        config_app.file_name = file_name
        config_app.vector_db_collections_id = vector_db_collections_id
        file_change_flag.set(not file_change_flag.get())
        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())
        
    @reactive.effect
    @reactive.event(file_change_flag, ignore_init=True)
    def showFile():
        
        outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'
        manuscript_file_path = Config.DIR_DATA / f'manuscript_{config_app.generated_files_id}.md'

        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        raw_outline = '\n'.join(createRawOutline(d_outline))
        
        # Cancel writing
        stream.latest_stream.cancel()

        # Show file name, outline and content
        updateFileNameFlag(config_app.file_name)
        ui.update_text(id='text_outline', value=raw_outline)

        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, outline_file_path, manuscript_file_path, write_n_contents=0), clear=True))

    def saveOutline(regenerate=False):

        def insertOutline(d, outline_items):

            if len(outline_items) == 1:
                d['content'] = d.get('content', []) + outline_items
                return d
            
            if outline_items[0] not in d:
                d[outline_items[0]] = {}
            
            d[outline_items[0]] = insertOutline(d[outline_items[0]].copy(), outline_items[1:])

            return d
        
        def processOutline(outline):

            d_outline, outline_items = {}, []
            chunks_leading_to_content = outline.split('<content>')
            for i, x in enumerate(chunks_leading_to_content):
                x = x.strip()
                if not x: continue
                text = ''
                for line_x in x.split('\n'):
            
                    line_x = line_x.strip()
                    if not line_x: continue
                    if not line_x.startswith('#'):
                        text += line_x
                        continue

                    if text: 
                        d_outline = insertOutline(d_outline.copy(), outline_items + [['content_user', text]])
                        text = ''
                    
                    hashes = line_x.split()[0]
                    header = ' '.join(line_x.split()[1:])
                    
                    if hashes != '#' * len(hashes):
                        ui.notification_show("'#'s must be followed by a space", type="error")
                        return False
                    
                    if len(hashes) > len(outline_items) + 1:
                        ui.notification_show(f"Expected no more than {len(outline_items) + 1} '#'s before {text}", type="error")
                        return False
                    
                    if len(hashes) <= len(outline_items):
                        outline_items = outline_items[:len(hashes)-1]

                    outline_items.append(header)
                    
                if text: 
                    d_outline = insertOutline(d_outline.copy(), outline_items + [['content_user', text]])
                    
                if i < len(chunks_leading_to_content)-1:
                    d_outline = insertOutline(d_outline.copy(), outline_items + [['content_ai', '']])

            return d_outline

        records = selectFromDB('generated_files', 
                            field_names=['id', 'file_name'], 
                            field_values=[[config_app.generated_files_id], [config_app.file_name]])
        
        if not (records.empty or regenerate): return True

        outline = input.text_outline().strip()
        if outline == '': return False

        # outline ='''
        # # Title: Neuroinflammation and Cognitive Function: Interplay of Causes, Mechanisms, and Pathological Outcomes
        # ##  Abstract
        # Neuroinflammation—once considered a secondary epiphenomenon of central nervous system (CNS) injury—is now recognized as an active, multifaceted driver of cognitive dysfunction across a broad spectrum of neurological and psychiatric disorders.
        # ## I. Introduction
        # continue writing
        # ### A. Defining Neuroinflammation: Beyond a simple response – complex cellular and molecular interactions <content>
        # ### B. Defining Cognitive Function: Key domains affected (memory, attention, executive function, processing speed) 
        # continue writing
        # <content>
        # continue writing
        # ### C. Historical Perspective vs. Current Understanding: Evolution of the concept of brain immunity and inflammation 
        # continue writing.
        # <content>
        # continue writing..
        # <content>
        # continue writing...
        # '''
    
        d_outline = processOutline(outline)

        with open(f'data/outline_{config_app.generated_files_id}.json', 'w') as fp:
            json.dump(d_outline, fp)

        current_time = datetime.now()
        
        updateDB('generated_files', 
                    update_fields=['status', 'create_date', 'update_date'], 
                    update_values=[generated_files_status.CREATED.value, current_time, current_time], 
                    select_fields=['id'], 
                    select_values=[[config_app.generated_files_id]])

        return True

    async def generateResponse(d_outline, outline_file_path, manuscript_file_path, write_n_contents=-1):

        def getHierarchy(d_outline, content_pre=[], current_section_list=[], counter=1):
            '''
            Get all previous content and current section hierarchy up to the point that needs ai generation
            '''

            is_gen_needed = False
            for k in d_outline:

                if k != 'content':
                    content_pre, current_section_list, is_gen_needed = getHierarchy(d_outline[k], 
                                                                content_pre + [f'{'#' * counter} {k}'],
                                                                current_section_list + [k],
                                                                counter + 1)
                    if not is_gen_needed: current_section_list.pop()
                else:
                    content_list = []
                    for v in d_outline[k]:
                        # Record only the first content_ai tag and 
                        # all content_user tags after that
                        if v[0] == 'content_ai':
                            if is_gen_needed: break
                            if v[1] == '': 
                                is_gen_needed = True
                            else:
                                content_pre.append(v[1])
                            content_list.append(v)
                        elif v[0] == 'content_user':
                            content_list.append(v)
                            if is_gen_needed: break
                            content_pre.append(v[1])
                    
                    if is_gen_needed: current_section_list.append(content_list)      
                
                if is_gen_needed: break
                        
            return content_pre, current_section_list, is_gen_needed
        
        def getSectionText(section_list):
            '''
            Get current section hierarchy up to the point that needs ai generation in markdown format 
            '''

            section_text_lines = []
            for i, v in enumerate(section_list):
                if not isinstance(v, list):
                    section_text_lines.append(f'{'#' * (i+1)} {v}')
                else:
                    for content_type, content in v:
                        if content_type == 'content_user' or content != '':
                            section_text_lines.append(content)
                        else:
                            section_text_lines.append('<content>')
            
            return '\n\n'.join(section_text_lines)
        
        def insertContent(d_outline, section_list, response):
            '''
            Inserts the ai response to the appropriate position of the outline
            '''

            if not len(section_list): return
            
            if len(section_list) == 1:
                for i, (content_type, content) in enumerate(section_list[0]):
                    if content_type == 'content_ai' and content == '':
                        d_outline['content'][i][1] = response
                        return
            else:
                insertContent(d_outline[section_list[0]], section_list[1:], response)
            
        len_last_content_pre, section_header = 0, None

        while True:

            content_pre, current_section_list, is_gen_needed = getHierarchy(d_outline)
            
            current_section = getSectionText(current_section_list)

            if section_header is None:
                section_header = content_pre
            else:
                section_header = content_pre[len_last_content_pre + 1:]
            
            section_header = '\n\n'.join(section_header) + '\n\n'

            len_last_content_pre = len(content_pre)
            
            yield section_header

            if not (write_n_contents != 0 and is_gen_needed): break
        
            #response = await config_app.agent.ainvoke({'content_pre': '\n\n'.join(content_pre), 'current_section': current_section}, {"configurable": {"thread_id": "abc123"}})
            
            #response = response['response']
            response = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse id erat lectus. Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis, lobortis justo sit amet, blandit libero. Suspendisse hendrerit sapien sit amet augue aliquam, at auctor purus mattis. In sed volutpat elit, et vehicula urna. Mauris libero lectus, dignissim quis facilisis aliquam, facilisis et tortor. Proin finibus lacus lectus, nec sodales ex vulputate in. Integer congue condimentum tempus. Ut ut elit in tellus viverra ornare at at nisl. Nam tincidunt vulputate pretium. Morbi purus purus, convallis in fringilla in, rhoncus a nisi. Curabitur eu pretium ligula. Vestibulum ullamcorper elit sit amet feugiat rutrum. Aenean tempor massa risus, non pulvinar justo scelerisque et. Maecenas non aliquet risus. Maecenas ac sem ut lorem commodo tempus.\nDonec eleifend tristique erat, sit amet sodales arcu ullamcorper eu. Aliquam non dapibus mi. Donec pretium risus ipsum, eu porttitor lectus porta in. Nulla facilisi. Proin rhoncus lectus nulla, non egestas sapien suscipit non. Maecenas bibendum semper cursus. Praesent in velit ut tellus tincidunt cursus laoreet et dolor. Morbi maximus maximus nunc nec luctus. Aenean ut sapien euismod, lacinia justo id, vestibulum ipsum.'

            insertContent(d_outline, current_section_list, response)
            
            print(response)
            
            tokens = response.split(' ')

            for i, s in enumerate(tokens):
                await asyncio.sleep(0.1 if not config_app.write_faster else 0.01)
                yield s + ' ' if i < len(tokens)-1 else s + '<a id="#custom-id"></a>\n\n'
            
            with open(outline_file_path, 'w') as fp:
                json.dump(d_outline, fp)

            with open(manuscript_file_path, 'w') as fp:
                fp.write('\n\n'.join(content_pre) + '\n\n' + response + '\n\n')
                ui.notification_show("Progress saved", type="message")

            current_time = datetime.now()

            updateDB('generated_files', 
                        update_fields=['status', 'update_date'], 
                        update_values=[generated_files_status.RUNNING.value, current_time], 
                        select_fields=['id'], 
                        select_values=[[config_app.generated_files_id]])
            
            if write_n_contents > 0: write_n_contents -= 1

    async def generate(regenerate):

        if config_app.file_name == '':
            ui.notification_show("Please save a file name.", type="error")
            return

        if not saveOutline(regenerate=regenerate): 
            ui.notification_show("Please provide an outline.", type="error")
            return

        outline_file_path = f'data/outline_{config_app.generated_files_id}.json'
        manuscript_file_path = f'data/manuscript_{config_app.generated_files_id}.md'

        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        await stream.stream(generateResponse(d_outline, outline_file_path, manuscript_file_path), clear=True)

        config_app.is_writing = True

    @reactive.effect
    @reactive.event(input.btn_resume_pause)
    async def resumeOrPause():

        if config_app.is_writing: 
            stream.latest_stream.cancel()
            return
        
        await generate(regenerate=False)

    @reactive.effect
    @reactive.event(input.btn_regenerate)
    async def startFromBeginning():
        await generate(regenerate=True)

    @reactive.effect
    def _():

        stream_status = stream.latest_stream.status()

        if stream_status in ["success", "error", "cancelled"]:

            if config_app.is_writing:

                current_time = datetime.now()
                updateDB('generated_files', 
                            update_fields=['status', 'update_date'], 
                            update_values=[stream_status, current_time], 
                            select_fields=['id'], 
                            select_values=[[config_app.generated_files_id]])
                
                reload_flag_sidebar.set(not reload_flag_sidebar.get())
                
                if stream_status == "success":
                    ui.notification_show("Writing finished", type="message")
                else:
                    ui.notification_show("Writing stopped", type="warning")

            config_app.is_writing = False

            ui.update_action_button("btn_resume_pause", icon=faicons.icon_svg("play"))
        else:
            ui.update_action_button("btn_resume_pause", icon=faicons.icon_svg("pause"))


    @reactive.effect
    @reactive.event(input.btn_speed)
    def speed():
        config_app.write_faster = not config_app.write_faster
        ui.update_action_button(
            "btn_speed", icon=faicons.icon_svg("person-walking" if config_app.write_faster else "person-running")
        )

    return content