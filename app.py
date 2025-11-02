from shiny import reactive
from shiny.express import ui, render, input, session, module
from shiny.types import ImgData
import faicons
from pathlib import Path
from src.frontend.main import mod_main
from src.frontend.authentication_modules.authentication import mod_authentication
from src.frontend.settings import mod_settings
from src.frontend.about import mod_about
from src.frontend.defaults import ConfigApp
from src.frontend.common import detachDocs, initProfile
from src.backend.db import selectFromDB, insertIntoDB, updateDB
from datetime import datetime
from utils import Config, print_func_name, getUIID
import asyncio

ui.include_css(Path(__file__).parent / "www" / "css" / "bootstrap.css", method='link_files')
ui.include_css(Path(__file__).parent / "www" / "css" / "bootstrap.min.css", method='link_files')
ui.include_css(Path(__file__).parent / "www" / "css" / "custom.css", method='link_files')

ui.page_opts(fillable=True, window_title=Config.APP_NAME)

config_app = ConfigApp()
config_app.session_id = session.id
login_status = reactive.value("logged_out")
reload_main_view_flag = reactive.value(True)
reload_settings_view_flag = reactive.value(True)
current_file_name = reactive.value('')

@module
def mod_account_options(input, output, session, logOut):

    with ui.div(class_='account-container'):
        if login_status.get() != 'logged_in':
            ui.input_action_button('btn_show_login', 'Login')
        else:
            with ui.div(class_='d-flex flex-column align-items-center gap-2'):
                ui.span(config_app.email, class_='d-flex align-items-center')
                ui.input_action_button('btn_logout', 'Logout')

    @reactive.effect
    @reactive.event(input.btn_logout)
    @print_func_name
    def logoutAfterLogoutBtnClick():
        logOut()
        ui.notification_show('Logged out.', type='message')

    @reactive.effect
    @reactive.event(input.btn_show_login)
    @print_func_name
    def logoutAfterShowLoginBtnClick():
        logOut()

with ui.div(class_="app-container"):
    with ui.div(class_='title-bar'):
        with ui.div(class_='col d-flex gap-3'):
            ui.span(faicons.icon_svg("pen-nib", width='25px'), class_='d-flex align-items-center')
            for c in Config.APP_NAME:
                ui.h4(c, style='color: #144545; margin: 0; text-shadow: 2px 2px 4px rgb(0 0 0 / 34%);')
            ui.span(faicons.icon_svg("pen-nib", width='25px'), class_='d-flex align-items-center')
            with ui.tooltip():
                ui.span('(Beta)')
                "This version is frequently tested and updated with new features for better performance. Some features may still be unstable."
            # with ui.div():
            #     @render.image()
            #     @print_func_name
            #     def icon():
            #         img: ImgData = {"src": str(Config.DIR_HOME / 'www' / 'assets' / f'logo.png'), 
            #                         "width": "100%"}
            #         return img
        @render.express
        @print_func_name
        def renderFileNameSaveOption():
            with ui.div(class_='col d-flex justify-content-end'):
                with ui.div(class_='d-flex gap-2'):
                    if login_status.get() in ['logged_in', 'guest']:                
                        with ui.tooltip(placement="top"):
                            with ui.div():
                                with ui.popover(placement='bottom', options={'trigger': 'focus'}):
                                    ui.input_action_button('btn_account', '', icon=faicons.icon_svg("user"))
                                    mod_account_options(getUIID('account'), logOut)
                            "Account"
                        with ui.tooltip(placement="top"):
                            ui.input_action_button('btn_settings', '', icon=faicons.icon_svg("gear"))
                            "Settings"
                    with ui.tooltip(placement="top"):
                        ui.input_action_button('btn_about', '', icon=faicons.icon_svg("question"))
                        "About"
    @render.express
    @print_func_name
    def renderView():
        if login_status.get() in ['logged_in', 'guest']:
            loadMainView()
        else:
            loadAuthView()
        
    ui.include_js(Config.DIR_HOME / "www" / "js" / "auth.js", method='inline')

@reactive.calc
def loadMainView():
    return mod_main(id='main', 
                config_app=config_app,
                reload_view_flag=reload_main_view_flag
        )

@reactive.calc
def loadAuthView():
    return mod_authentication(id='auth', config_app=config_app, changeLoginStatus=changeLoginStatus)

@reactive.effect
@reactive.event(input.email)
@print_func_name
def loadCachedEmail():

    if not input.email(): return
    config_app.email = input.email()
    changeLoginStatus('logged_in')

@print_func_name
def changeLoginStatus(status):
    login_status.set(status)
    initProfile(config_app)
    reload_settings_view_flag.set(not reload_settings_view_flag.get())
    reload_main_view_flag.set(not reload_main_view_flag.get())
    
@print_func_name
def logOut():

    loop = asyncio.get_event_loop()
    loop.create_task(session.send_custom_message('auth_key', {'email': ''}))

    config_app = ConfigApp()
    config_app.session_id = session.id
    reload_settings_view_flag.set(not reload_settings_view_flag.get())
    reload_main_view_flag.set(not reload_main_view_flag.get())

    login_status.set('logged_out')

@reactive.effect
@reactive.event(input.btn_settings)
@print_func_name
def showSettings():

    settings_view = mod_settings(id=getUIID('settings'), 
                                 callback_fn=changeSettings,
                                 config_app=config_app, 
                                 reload_flag=reload_settings_view_flag
    )

    m = ui.modal(
        settings_view,
        title="",
        easy_close=False,
        footer=None,
        size='l'
    )

    ui.modal_show(m)

@reactive.effect
@reactive.event(input.btn_about)
@print_func_name
def showAbout():

    about_view = mod_about(id=getUIID('about'))

    m = ui.modal(
        about_view,
        title="About",
        easy_close=True,
        footer=None,
        size='xl'
    )

    ui.modal_show(m)

    return 

@print_func_name
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
                    field_names=['email', 'session', 'llm', 'temperature', 'instructions', 'create_date', 'update_date'], 
                    field_values=[[config_app.email], [config_app.session_id], [config_app.llm], [config_app.temperature], [config_app.instructions], [current_time], [current_time]])
        
        initProfile(config_app)

    else:
        updateDB(table_name='settings',
                update_fields=['session', 'llm', 'temperature', 'instructions', 'update_date'],
                update_values=[config_app.session_id, config_app.llm, config_app.temperature, config_app.instructions, current_time],
                select_fields=['id'],
                select_values=[[config_app.settings_id]]
        )

@print_func_name
def changeSettings():

    saveSettingsToDB()
    
    if config_app.generated_files_id and config_app.vector_db_collections_id:
        detachDocs(config_app.generated_files_id, config_app.vector_db_collections_id)
        config_app.vector_db_collections_id = None

    if config_app.generated_files_id and config_app.vector_db_collections_id_lit_search:
        detachDocs(config_app.generated_files_id, config_app.vector_db_collections_id_lit_search)
        config_app.vector_db_collections_id_lit_search = None

    reload_settings_view_flag.set(not reload_settings_view_flag.get())
    reload_main_view_flag.set(not reload_main_view_flag.get())