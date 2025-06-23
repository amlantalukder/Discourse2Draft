from shiny import reactive
from shiny.express import ui, render, module
import faicons
from ..db import selectFromDB, updateDB, \
                generated_files_status, \
                Config as db_config
from ..common import getFileType, getFileTypeIcon, getVectorDBFiles, detachDocs, getGeneratedDocuments
import pandas as pd
from utils import Config
from datetime import datetime

@module
def getGeneratedDocItemView(input, output, session, info, show_expanded_view, setCurrentFile, reload_flag_parent_view):

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
        reload_flag_parent_view.set(not reload_flag_parent_view.get())

    @reactive.effect
    @reactive.event(input.btn_delete_rag, ignore_init=True)
    def applyDetachDocs():
        detachDocs(generated_files_id = info['id'], vector_db_collections_id = info['vector_db_collections_id'])
        reload_flag_parent_view.set(not reload_flag_parent_view.get())
    
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
                    with ui.tooltip():
                        ui.input_action_link('btn_show', info['file_name'], class_='cut-text')
                        info['file_name']
                with ui.div(class_='app-td col-2'):
                    ui.span(db_config.generated_files_status_desc[info['status']])
                with ui.div(class_='app-td col-2'):
                    @render.express
                    def showAttachedFiles():
                        file_names = getVectorDBFiles(info['vector_db_collections_id'])
                        if not file_names: return
                        with ui.div(class_='border rounded p-2'):
                            with ui.div():
                                for i, file_name in enumerate(file_names):
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
def mod_genererated_doc_detailed_view(input, output, session, config_app, setCurrentFile):

    reload_flag = reactive.value(True)

    @reactive.calc
    @reactive.event(reload_flag)
    def getDocs():
        records = getGeneratedDocuments(email=config_app.email, session_id=config_app.session_id)
        if records.empty: return ui.span('No documents')
        records_settings = selectFromDB(table_name='settings',
                            field_names=['id'],
                            field_values=[list(map(int, records['settings_id'].unique()))])
        records = pd.merge(left=records, 
                            right=records_settings[['id', 'llm', 'temperature', 'instructions']], 
                            left_on='settings_id', right_on='id', how='left',
                            suffixes=[None, '_settings'])
        return records
    
    @render.express
    def showView():
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
                        getGeneratedDocItemView(f'doc_list_item_exp_view_{i}', 
                                            info=row, 
                                            show_expanded_view=True,
                                            setCurrentFile=setCurrentFile, 
                                            reload_flag_parent_view=reload_flag)
                    