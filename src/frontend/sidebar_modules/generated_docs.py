from shiny import reactive
from shiny.express import ui, render, module
import faicons
from utils import Config, getUIID, print_func_name
from ...backend.db import updateDB, \
                generated_files_status, \
                generated_files_ai_architecture, \
                Config as db_config
from ..common import getFileType, getFileTypeIcon, getVectorDBFiles, detachDocs, getGeneratedDocuments, getDocContent
from ...backend.ai.architecture import Architecture
from datetime import datetime

@module
def getGeneratedDocItemView(input, output, session, 
                            info, show_expanded_view,
                            config_app, 
                            reload_content_view_flag,
                            reload_generated_docs_view_flag,
                            reload_generated_docs_detailed_view_flag=None):
    
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
                    @print_func_name
                    async def renderDownloadDoc():
                        attached_files = applyGetVectorDBFiles()
                        content = getDocContent(file_id=info['id'], attached_files=attached_files)
                        if content is None: return
                        yield content
                with ui.div(class_='col-auto d-flex align-items-center'):
                    ui.input_action_button(f'btn_delete', '', icon=faicons.icon_svg('trash'))
        else:
            with ui.div(class_='app-tr row'):
                with ui.div(class_='app-td col'):
                    with ui.tooltip():
                        ui.input_action_link('btn_show', info['file_name'], class_='cut-text')
                        info['file_name']
                with ui.div(class_='app-td col-2'):
                    ui.span(db_config.generated_files_status_desc[info['status']])
                with ui.div(class_='app-td col-2'):
                    @render.express
                    def renderAttachedFiles():
                        files = applyGetVectorDBFiles()
                        if not files: return
                        with ui.div(class_='border rounded p-2'):
                            with ui.div():
                                for i, (_, file_name) in enumerate(files):
                                    with ui.div(class_='d-flex gap-1'):
                                        with ui.div(class_='col-2 d-flex align-items-center'):
                                            getFileTypeIcon(f'icon_{i}', file_type=getFileType(file_name))
                                        with ui.div(class_='col d-flex align-items-center'):
                                            with ui.tooltip():
                                                ui.span(file_name, class_='cut-text')
                                                file_name
                            with ui.div(class_='text-end'):
                                with ui.tooltip():
                                    ui.input_action_link(f'btn_delete_rag', '', icon=faicons.icon_svg('trash'))
                                    "De-attach documents"

                with ui.div(class_='app-td col-2'):
                    with ui.div(class_='d-flex flex-column'):
                        with ui.div(class_='d-flex gap-1'):
                            ui.strong('LLM:')
                            ui.span(info['llm'])
                        with ui.div(class_='d-flex gap-1'):
                            ui.strong('Temperature:')
                            ui.span(info['temperature'])
                        with ui.div():
                            ui.strong('Instructions:')
                            with ui.div(class_='d-flex'):
                                ui.span(info['instructions'], class_='cut-text')
                                with ui.popover(options={'trigger': 'focus'}):
                                    ui.input_action_link('dummy', 'more')
                                    with ui.div(class_='popover-instructions'):
                                        ui.markdown(info['instructions'])
                with ui.div(class_='app-td col-1'):
                    ui.span(info['create_date'].strftime('%Y-%m-%d %H:%M:%S'))
                with ui.div(class_='app-td col-1'):
                    ui.span(info['update_date'].strftime('%Y-%m-%d %H:%M:%S'))
                with ui.div(class_='app-td col-1 justify-content-center'):
                    with ui.div():
                        @render.download(label=faicons.icon_svg("download"), filename='manuscript.md')
                        @print_func_name
                        async def renderDownloadDoc():
                            attached_files = applyGetVectorDBFiles()
                            content = getDocContent(file_id=info['id'], attached_files=attached_files)
                            if content is None: return
                            yield content
                with ui.div(class_='app-td col-1 justify-content-center'):
                    with ui.div():
                        ui.input_action_button(f'btn_delete', '', icon=faicons.icon_svg('trash'))

    @reactive.calc
    @print_func_name
    def applyGetVectorDBFiles():
        return getVectorDBFiles(info['vector_db_collections_id_uploaded_files'])

    @reactive.effect
    @reactive.event(input.btn_show, ignore_init=True)
    @print_func_name
    def showFile():

        # If invoked from the generated files detailed view
        ui.modal_remove()

        int_ = lambda x: x if x is None else int(x)
        
        config_app.generated_files_id = info['id']
        config_app.file_name = info['file_name']
        config_app.vector_db_collections_id = int_(info['vector_db_collections_id_uploaded_files'])
        config_app.vector_db_collections_id_lit_search = int_(info['vector_db_collections_id_literature'])
        config_app.llm = info['llm']
        config_app.temperature = info['temperature']
        config_app.instructions = info['instructions']
        
        match info['ai_architecture']:

            case generated_files_ai_architecture.BASE.value:

                config_app.agent = Architecture(model_name=config_app.llm, 
                                                temperature=config_app.temperature, 
                                                instructions=config_app.instructions, 
                                                type=generated_files_ai_architecture.BASE.value).agent
            
            case generated_files_ai_architecture.RAG.value:

                vector_db_collection_name, vector_db_collection_name_lit_search = '', ''
                
                if config_app.vector_db_collections_id:
                    vector_db_collection_name = f'{Config.APP_NAME_AS_PREFIX}_collection_{int(config_app.vector_db_collections_id)}'
                
                if config_app.vector_db_collections_id_lit_search:
                    vector_db_collection_name_lit_search = f'{Config.APP_NAME_AS_PREFIX}_collection_{int(config_app.vector_db_collections_id_lit_search)}'

                config_app.agent = Architecture(model_name=config_app.llm, 
                                                temperature=config_app.temperature, 
                                                instructions=config_app.instructions, 
                                                type=generated_files_ai_architecture.RAG.value, 
                                                collection_name=vector_db_collection_name,
                                                collection_name_lit_search=vector_db_collection_name_lit_search).agent

        reload_content_view_flag.set(not reload_content_view_flag.get())

    @reactive.effect
    @reactive.event(input.btn_delete, ignore_init=True)
    @print_func_name
    def deleteFile():
        updateDB('generated_files', 
                update_fields=['status', 'update_date'], 
                update_values=[generated_files_status.DELETED.value, datetime.now()], 
                select_fields=['id'], 
                select_values=[[info['id']]])
        if reload_generated_docs_detailed_view_flag:
            reload_generated_docs_detailed_view_flag.set(not reload_generated_docs_detailed_view_flag.get())
        reload_generated_docs_view_flag.set(not reload_generated_docs_view_flag.get())

        # If the deleted file was selected in the content, clear the content
        if config_app.generated_files_id == info['id']:

            config_app.generated_files_id = None
            config_app.file_name = ''
            config_app.vector_db_collections_id = None

            reload_content_view_flag.set(not reload_content_view_flag.get())

    @reactive.effect
    @reactive.event(input.btn_delete_rag, ignore_init=True)
    @print_func_name
    def applyDetachDocs():
        detachDocs(generated_files_id = info['id'], vector_db_collections_id = info['vector_db_collections_id_uploaded_files'])
        reload_generated_docs_detailed_view_flag.set(not reload_generated_docs_detailed_view_flag.get())

    return content

@module
def mod_generated_docs_detailed_view(input, output, session, config_app, reload_content_view_flag, reload_view_flag, reload_parent_view_flag):

    with ui.hold() as content:
        @render.express
        @print_func_name
        def renderView():
            records = getDocs()

            with ui.div(class_='app-table-container'):
                with ui.div(class_='app-table'):
                    with ui.div(class_='app-thead'):
                        with ui.div(class_='app-tr row'):
                            with ui.div(class_='app-th col'):
                                ui.strong('Document')
                            with ui.div(class_='app-th col-2'):
                                ui.strong('Status')
                            with ui.div(class_='app-th col-2'):
                                ui.strong('Attached documents')
                            with ui.div(class_='app-th col-2'):
                                ui.strong('Settings')
                            with ui.div(class_='app-th col-1'):
                                ui.strong('Create date')
                            with ui.div(class_='app-th col-1'):
                                ui.strong('Update date')
                            with ui.div(class_='app-th col-1 justify-content-center'):
                                ""
                            with ui.div(class_='app-th col-1 justify-content-center'):
                                ""
                    with ui.div(class_='app-tbody'):
                        for i, row in records.iterrows():
                            getGeneratedDocItemView(getUIID('doc_list_item_exp_view'), 
                                                info=row, 
                                                show_expanded_view=True,
                                                config_app=config_app,
                                                reload_content_view_flag=reload_content_view_flag, 
                                                reload_generated_docs_view_flag=reload_parent_view_flag,
                                                reload_generated_docs_detailed_view_flag=reload_view_flag)

    @reactive.calc
    @reactive.event(reload_view_flag)
    @print_func_name
    def getDocs():

        return getGeneratedDocuments(email=config_app.email, session_id=config_app.session_id)
                            
    return content

@module
def mod_generated_docs_view(input, output, session, config_app, reload_content_view_flag, reload_view_flag, reload_detailed_view_flag):

    with ui.div(class_='side-bar-docs-container'):
                        
        @render.express
        @print_func_name
        def showGeneratedDocuments():

            records = getDocs()
        
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
                        getGeneratedDocItemView(getUIID('doc_list_item'), 
                                        info=row,
                                        show_expanded_view=False,
                                        config_app=config_app,
                                        reload_content_view_flag = reload_content_view_flag, 
                                        reload_generated_docs_view_flag=reload_view_flag)
        
    @reactive.calc()
    @reactive.event(reload_view_flag)
    @print_func_name
    def getDocs():

        return getGeneratedDocuments(email=config_app.email, session_id=config_app.session_id)

    @reactive.effect
    @reactive.event(input.btn_show_generated_docs_details)
    @print_func_name
    def showDetailedGeneratedDocsView():

        generated_docs_detailed_view = mod_generated_docs_detailed_view(id=getUIID('generated_docs_detailed'), 
                                                                        config_app=config_app,
                                                                        reload_content_view_flag=reload_content_view_flag,
                                                                        reload_view_flag=reload_detailed_view_flag,
                                                                        reload_parent_view_flag=reload_view_flag)

        m = ui.modal(
            generated_docs_detailed_view,
            title="Generated documents",
            easy_close=True,
            footer=None,
            size='xl'
        )

        ui.modal_show(m)