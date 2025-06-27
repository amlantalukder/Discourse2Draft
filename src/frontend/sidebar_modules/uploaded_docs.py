from shiny import reactive
from shiny.express import ui, module, render, expressify
import faicons
from ..common import getFileType, getFileTypeIcon
from ..db import selectFromDB, updateDB, \
                uploaded_files_status, \
                vector_db_collections_status, \
                generated_files_status
from datetime import datetime

@module
def getUploadedDocItemView(input, output, session, doc, is_selected, changeSelectedDocs, select_all_docs, reload_sidebar_view_flag, showDetailedGeneratedDocs):

    @reactive.effect
    @reactive.event(input.chk_file, ignore_init=True)
    def addOrRemoveDoc():
        print('add or remove doc')
        print((doc['id'], doc['file_name']), input.chk_file())
        changeSelectedDocs(doc['id'], doc['file_name'], input.chk_file())

    @reactive.effect
    @reactive.event(select_all_docs, ignore_init=True)
    def addOrRemoveDocSelectAll():
        ui.update_checkbox(id='chk_file', value=select_all_docs.get())

    @reactive.effect
    @reactive.event(input.btn_show_detailed_generated_docs)
    def showGeneratedDocs():
        showDetailedGeneratedDocs()

    def showDeleteFileConfirmationDialog(generated_file_name_list):

        @expressify
        def showView():
            with ui.div():

                ui.span("This document is being used by the following files.") 

                @render.express
                def showFiles():
                    for file_name in generated_file_name_list:
                        with ui.div(class_='d-flex ms-2 gap-2'):
                            ui.span(faicons.icon_svg("hand-point-right", "regular"))
                            file_name

                ui.span("To remove the document, please", class_='me-1')
                ui.input_action_link(id='btn_show_detailed_generated_docs', label="de-attach this document", class_='me-1')
                ui.span("from these files.")

        with ui.hold() as content:
            showView()

        ui.notification_show(content, type='message', duration=10)

    def checkIfDocIsUnderUse() -> list:

        records = selectFromDB(table_name='vector_db_collection_files',
                     field_names=['uploaded_files_id'],
                     field_values=[[doc['id']]])
        
        if not records.empty:

            records = selectFromDB(table_name='vector_db_collections',
                                   field_names=['id', 'status'],
                                   field_values=[list(map(int, records['vector_db_collections_id'].unique())), [vector_db_collections_status.ACTIVE.value]])
            
            if not records.empty:

                valid_file_statuses = list({e.value for e in generated_files_status} - {generated_files_status.DELETED.value})

                records = selectFromDB(table_name='generated_files',
                                       field_names=['vector_db_collections_id', 'status'],
                                       field_values=[list(map(int, records['id'].unique())), valid_file_statuses])
                
                return list(records['file_name'].values)
            
        return []

    @reactive.effect
    @reactive.event(input.btn_delete, ignore_init=True)
    def showDeleteFileConfirmation():
        
        files_that_use_this_doc = checkIfDocIsUnderUse()

        if files_that_use_this_doc:
            showDeleteFileConfirmationDialog(files_that_use_this_doc)
        else:
            deleteFile()

    def deleteFile():
        updateDB(table_name='uploaded_files', 
                update_fields=['status', 'update_date'], 
                update_values=[uploaded_files_status.DELETED.value, datetime.now()], 
                select_fields=['id'], 
                select_values=[[doc['id']]])
        
        reload_sidebar_view_flag.set(not reload_sidebar_view_flag.get())
    
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