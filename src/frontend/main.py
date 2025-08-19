from shiny import reactive
from shiny.express import ui, render, module
from utils import getUIID, print_func_name
from ..backend.db import insertIntoDB, updateDB, selectFromDB, \
                generated_files_status, \
                generated_files_ai_architecture
from .manage_outline import mod_outline_manager, mod_ai_outline_creator
from .contents import mod_contents
from .sidebar_modules.sidebar import mod_sidebar
from .common import initProfile
import json
from datetime import datetime

@module
def mod_main(input, output, session, config_app, reload_main_view_flag, reload_generated_docs_view_flag, settings_changed_flag):

    reload_content_view_flag = reactive.value(True)
    reload_rag_and_ref_flag = reactive.value(True)
    file_change_flag = reactive.value(False)

    reload_uploaded_docs_view_flag = reactive.value(True)

    outline_from_outline_manager = reactive.value('')
    outline_creator_options = reactive.value({'show': False,
                                              'show_init_view': True
                                              })

    with ui.div(class_='app-body-container'):
        with ui.layout_sidebar():
            with ui.sidebar(id='sidebar_docs', position="left", open='closed' if config_app.email == '' else 'open', bg="#f8f8f8", width=400):
                @render.express
                @print_func_name
                def renderSideBar():
                    mod_sidebar(id=getUIID('sidebar'), 
                                config_app=config_app, 
                                reload_rag_and_ref_flag=reload_rag_and_ref_flag, 
                                reload_content_view_flag=reload_content_view_flag, 
                                reload_generated_docs_view_flag=reload_generated_docs_view_flag,
                                reload_uploaded_docs_view_flag=reload_uploaded_docs_view_flag)

            with ui.div(class_='app-body'):
                @render.express
                @print_func_name
                def renderView():
                    content_view, outline_creator_view = loadViews()
                    options = outline_creator_options.get()
                    if options['show']:
                        outline_creator_view
                    else:
                        content_view
                        

    @reactive.calc
    @print_func_name
    def loadViews():
        content_view = mod_contents('contents', 
                         config_app, 
                         outline_from_outline_manager, 
                         reload_content_view_flag, 
                         reload_rag_and_ref_flag, 
                         reload_generated_docs_view_flag, 
                         file_change_flag, 
                         settings_changed_flag)
        outline_creator_view = mod_ai_outline_creator('ai_outline_creator', 
                                                    outline_creator_options, 
                                                    saved_outline=outline_from_outline_manager,
                                                    config_app=config_app,
                                                    reload_uploaded_docs_view_flag=reload_uploaded_docs_view_flag)
        
        return content_view, outline_creator_view

    @reactive.effect
    @reactive.event(input.btn_new_file)
    @print_func_name
    def showNewFile():
        config_app.file_name = ''
        config_app.generated_files_id = None
        config_app.vector_db_collections_id = None
        initProfile(config_app)

        reload_main_view_flag.set(not reload_main_view_flag.get())

    @reactive.effect
    @reactive.event(input.btn_save_file_name)
    @print_func_name
    def saveFileName():
        file_name = input.text_file_name()

        if config_app.file_name == file_name: return

        valid_file_statuses = list({e.value for e in generated_files_status} - {generated_files_status.DELETED.value})
        if config_app.email != '':
            records = selectFromDB('generated_files', 
                                field_names=['email', 'file_name', 'status'], 
                                field_values=[[config_app.email], [file_name], valid_file_statuses])
        else:
            records = selectFromDB('generated_files', 
                                field_names=['session', 'file_name', 'status'], 
                                field_values=[[config_app.session], [file_name], valid_file_statuses])
        
        if not records.empty:
            ui.notification_show('File name already exists.', type='error')
            return 
        
        current_time = datetime.now()

        if config_app.generated_files_id:
            
            updateDB(table_name='generated_files',
                    update_fields=['file_name', 'update_date'],
                    update_values=[file_name, current_time],
                    select_fields=['id'],
                    select_values=[[config_app.generated_files_id]])
            
            config_app.file_name = file_name

        else:
            ids = insertIntoDB(table_name='generated_files', 
                        field_names=['email', 'session', 'settings_id', 'ai_architecture', 'file_name', 'status', 'create_date', 'update_date'], 
                        field_values=[[config_app.email], [config_app.session_id], [config_app.settings_id], [generated_files_ai_architecture.BASE.value], [file_name], 
                                    'created', [current_time], [current_time]])
            
            config_app.generated_files_id = ids[0]
            config_app.file_name = file_name

            outline_file_path = f'data/outline_{config_app.generated_files_id}.json'

            with open(outline_file_path, 'w') as fp:
                json.dump({}, fp)
            
            settings_changed_flag.set(not settings_changed_flag.get())

        reload_generated_docs_view_flag.set(not reload_generated_docs_view_flag.get())
        
        ui.notification_show('File name saved.', type='message')

    @reactive.effect
    @reactive.event(input.btn_open_outline_manager)
    @print_func_name
    def openOutlineManager():

        outline = input.text_outline().strip()
        if outline == '': return False

        outline_manager_view = mod_outline_manager(getUIID('outline_manager'), 
                                                   outline=outline, 
                                                   saved_outline=outline_from_outline_manager,
                                                   close_fn=ui.modal_remove)

        m = ui.modal(
            outline_manager_view,
            title="",
            easy_close=False,
            footer=None,
            size='xl',
            style='height: 90vh'
        )

        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.btn_open_outline_creator)
    @print_func_name
    def openOutlineCreator():
        outline_creator_options.set({'show': True, 'show_init_view': False})

    @reactive.effect
    @reactive.event(reload_main_view_flag)
    @print_func_name
    def reloadMainView():

        outline_creator_options.set({'show': True, 'show_init_view': True})
        file_change_flag.set(not file_change_flag.get())
        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())
        
    @reactive.effect
    @reactive.event(reload_content_view_flag, ignore_init=True)
    @print_func_name
    def reloadContentView():
        outline_creator_options.set({'show': False, 'show_init_view': False})
        