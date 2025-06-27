from shiny import reactive
from shiny.express import ui, render, input, session
import faicons
from pathlib import Path
from src.frontend.main import mod_main
from src.frontend.authentication_modules.authentication import mod_authentication
from src.frontend.settings import mod_settings
from src.frontend.defaults import ConfigApp
from src.frontend.db import selectFromDB, insertIntoDB, updateDB, generated_files_status, generated_files_ai_architecture
from datetime import datetime
from utils import Config
import json
import asyncio

ui.include_css(Path(__file__).parent / "www" / "css" / "bootstrap.css", method='link_files')
ui.include_css(Path(__file__).parent / "www" / "css" / "bootstrap.min.css", method='link_files')
ui.include_css(Path(__file__).parent / "www" / "css" / "custom.css", method='link_files')

ui.page_opts(title='', fillable=True, window_title=Config.APP_NAME)

config_app = ConfigApp()
config_app.session_id = session.id
login_status = reactive.value("logged_out")
reload_content_view_flag = reactive.value(True)
reload_sidebar_view_flag=reactive.value(True)
settings_changed_flag_main_view = reactive.value(True)
reload_flag_settings_view = reactive.value(True)
current_file_name = reactive.value('')

def updateFileNameFlag(file_name):
    current_file_name.set(file_name)

@reactive.effect
def loadViews():
    global auth_view, main_view, settings_view
    auth_view = mod_authentication(id="auth", config_app=config_app, changeLoginStatus=changeLoginStatus)
    main_view = mod_main(id=f"main", 
                         config_app=config_app, 
                         updateFileNameFlag=updateFileNameFlag,
                         reload_content_view_flag=reload_content_view_flag,
                         reload_sidebar_view_flag=reload_sidebar_view_flag, 
                         settings_changed_flag=settings_changed_flag_main_view,
    )
    
    settings_view = mod_settings(id=f'settings', 
                                 callback_fn=changeSettings, 
                                 config_app=config_app, 
                                 reload_flag=reload_flag_settings_view
    )

@reactive.effect
@reactive.event(input.btn_save_file_name)
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
        
        settings_changed_flag_main_view.set(not settings_changed_flag_main_view.get())
    reload_sidebar_view_flag.set(not reload_sidebar_view_flag.get())
    ui.notification_show('File name saved.', type='message')

@reactive.effect
@reactive.event(input.btn_new_file)
def showNewFile():
    config_app.file_name = ''
    reload_content_view_flag.set(not reload_content_view_flag.get())

@reactive.effect
@reactive.event(current_file_name)
def updateFileName():
    ui.update_text(id='text_file_name', value=current_file_name.get())

def logIn():
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

def changeLoginStatus(status):
    login_status.set(status)
    logIn()
    reload_flag_settings_view.set(not reload_flag_settings_view.get())
    settings_changed_flag_main_view.set(not settings_changed_flag_main_view.get())
    
def logOut():

    loop = asyncio.get_event_loop()
    loop.create_task(session.send_custom_message('auth_key', {'email': ''}))

    config_app.setDefaults()
    config_app.session_id = session.id
    reload_flag_settings_view.set(not reload_flag_settings_view.get())
    settings_changed_flag_main_view.set(not settings_changed_flag_main_view.get())

    login_status.set('logged_out')

@reactive.effect
@reactive.event(input.btn_logout)
def _():
    logOut()
    ui.notification_show('Logged out.', type='message')

@reactive.effect
@reactive.event(input.btn_show_login)
def _():
    logOut()

@reactive.effect
@reactive.event(input.btn_settings)
def showSettings():

    m = ui.modal(
        settings_view,
        title="",
        easy_close=False,
        footer=None,
        size='l'
    )

    ui.modal_show(m)

def saveSettingsToDB():

    current_time = datetime.now()

    # ----------------------------------------------------------------------------------------
    # New settings record is created on two occassions,
    # 1. If there is no saved settings for the current session or email i.e. config_app.settings_id is None
    # 2. If there is a saved settings and it is not attached to any generated file. i.e. records_generated_files is empty
    # Otherwise update the current settings.
    # ----------------------------------------------------------------------------------------
    records_generated_files = None
    if config_app.settings_id is not None:
        records_generated_files = selectFromDB(table_name='generated_files', field_names=['settings_id'], field_values=[[config_app.settings_id]])
    if config_app.settings_id is None or (records_generated_files is not None and not records_generated_files.empty):
        insertIntoDB(table_name='settings', 
                    field_names=['email', 'session', 'llm', 'temperature', 'instructions', 'update_date'], 
                    field_values=[[config_app.email], [config_app.session_id], [config_app.llm], [config_app.temperature], [config_app.instructions], [current_time]])
        
        logIn()

    else:
        updateDB(table_name='settings',
                update_fields=['session', 'llm', 'temperature', 'instructions', 'update_date'],
                update_values=[config_app.session_id, config_app.llm, config_app.temperature, config_app.instructions, current_time],
                select_fields=['id'],
                select_values=[[config_app.settings_id]]
        )

def changeSettings():

    saveSettingsToDB()
    
    reload_flag_settings_view.set(not reload_flag_settings_view.get())
    settings_changed_flag_main_view.set(not settings_changed_flag_main_view.get())


with ui.div(class_="app-container"):
    with ui.div(class_='row title-bar'):
        with ui.div(class_='col'):
            ui.h4(Config.APP_NAME)
        @render.express
        def showFileNameSaveOption():
            if login_status.get() in ['logged_in', 'guest']:
                with ui.div(class_='col file-name'):
                    ui.input_text('text_file_name', 'File Name', value=config_app.file_name),
                    ui.input_action_button('btn_save_file_name', 'Save')
                with ui.div(class_='col d-flex justify-content-end'):
                    with ui.div(class_='d-flex gap-2'):
                        with ui.tooltip(placement="top"):
                            ui.input_action_button('btn_new_file', '', icon=faicons.icon_svg("plus"))
                            "New File"
                        with ui.tooltip(placement="top"):
                            with ui.div():
                                with ui.popover(placement='bottom', options={'trigger': 'focus'}):
                                    ui.input_action_button('btn_account', '', icon=faicons.icon_svg("user"))
                                    with ui.div(class_='account-container'):
                                        @render.express
                                        def showAccountInfo():
                                            if login_status.get() != 'logged_in':
                                                ui.input_action_button('btn_show_login', 'Login')
                                            else:
                                                with ui.div(class_='d-flex flex-column align-items-center gap-2'):
                                                    ui.span(config_app.email, class_='d-flex align-items-center')
                                                    ui.input_action_button('btn_logout', 'Logout')
                            "Account"
                        with ui.tooltip(placement="top"):
                            ui.input_action_button('btn_settings', '', icon=faicons.icon_svg("gear"))
                            "Settings"
            else:
                # Without this empty div, there is an empty shin-html-output element,
                # for which the header does not align center.
                with ui.div(class_="col"):
                    ""
    @render.ui
    def showView():
        if login_status.get() in ['logged_in', 'guest']:
            return main_view
        else:
            return auth_view
        
    ui.include_js(Config.DIR_HOME / "www" / "js" / "auth.js", method='inline')