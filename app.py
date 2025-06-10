from shiny import reactive
from shiny.express import ui, render, input, session
import faicons
from pathlib import Path
from src.frontend.main import mod_main
from src.frontend.authentication_modules.authentication import mod_authentication
from src.frontend.settings import mod_settings
from src.frontend.defaults import ConfigApp
from src.frontend.db import selectFromDB, updateDB
from datetime import datetime
from utils import Config
import asyncio

ui.include_css(Path(__file__).parent / "www" / "css" / "bootstrap.css", method='link_files')
ui.include_css(Path(__file__).parent / "www" / "css" / "bootstrap.min.css", method='link_files')
ui.include_css(Path(__file__).parent / "www" / "css" / "custom.css", method='link_files')

ui.page_opts(title="", fillable=True)

config_app = ConfigApp()
config_app.session_id = session.id
login_status = reactive.value("logged_out")
settings_flag = reactive.value(True)
reset_flag = reactive.value(True)
current_file_name = reactive.value('')

def updateFileNameFlag(file_name):
    current_file_name.set(file_name)

@reactive.effect
def loadViews():
    global main_view, auth_view
    main_view = mod_main(id="main", config_app=config_app, updateFileNameFlag=updateFileNameFlag, reset_flag=reset_flag)
    auth_view = mod_authentication(id="auth", config_app=config_app, changeLoginStatus=changeLoginStatus)

@reactive.effect
@reactive.event(input.btn_save_file_name)
def saveFileName():
    file_name = input.text_file_name()

    if config_app.file_name == file_name: return

    records = selectFromDB('generated_files', 
                        field_names=['email', 'session', 'file_name'], 
                        field_values=[[config_app.email], [config_app.session_id], [config_app.file_name]])
    if not records.empty:
        ui.notification_show('File name already exists.', type='error')
        return    

    config_app.file_name = file_name
    ui.notification_show('File name saved.', type='message')

@reactive.effect
@reactive.event(input.btn_new_file)
def showNewFile():
    config_app.file_name = ''
    reset_flag.set(not reset_flag.get())

@reactive.effect
@reactive.event(current_file_name)
def updateFileName():
    ui.update_text(id='text_file_name', value=current_file_name.get())

def logIn():
    records = selectFromDB('settings', 
                field_names=['email'],
                field_values=[[config_app.email]])

    config_app.llm = records['llm'].iloc[0]
    config_app.temperature = float(records['temperature'].iloc[0])
    config_app.instructions = records['instructions'].iloc[0]

    settings_flag.set(not settings_flag.get())
    reset_flag.set(not reset_flag.get())

def changeLoginStatus(status):
    login_status.set(status)
    if login_status.get() == 'logged_in': logIn()

def logOut():

    loop = asyncio.get_event_loop()
    loop.create_task(session.send_custom_message('auth_key', {'email': ''}))

    config_app.setDefaults()
    config_app.session_id = session.id
    settings_flag.set(not settings_flag.get())
    reset_flag.set(not reset_flag.get())

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
@reactive.event(settings_flag)
def getDialogs():
    global settings_content
    settings_content = mod_settings(id='settings', callback_fn=changeSettings, config_app=config_app)

@reactive.effect
@reactive.event(input.btn_settings)
def showSettings():

    m = ui.modal(
        settings_content,
        title="",
        easy_close=False,
        footer=None,
        size='l'
    )

    ui.modal_show(m)

def changeSettings():

    current_time = datetime.now()

    updateDB('settings', 
                update_fields=['llm', 'temperature', 'instructions', 'update_date'], 
                update_values=[config_app.llm, config_app.temperature, config_app.instructions, current_time],
                select_fields=['email'],
                select_values=[[config_app.email]])
    
    settings_flag.set(not settings_flag.get())
    reset_flag.set(not reset_flag.get())


with ui.div(class_="app-container"):
    with ui.div(class_='row title-bar'):
        with ui.div(class_='col'):
            ui.h4('AI Word processor')
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