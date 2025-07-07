from shiny import reactive
from shiny.express import module, ui, render
from .login import mod_login
from .create_account import mod_create_account
from .forgot_password import mod_forgot_password
from utils import print_func_name, getUIID

# -----------------------------------------------------------------------
@module
def mod_authentication(input, output, session, config_app, changeLoginStatus):

    view = reactive.value('login')

    @print_func_name
    def changeView(value):
        view.set(value)

    with ui.div(class_='app-dialog-container'):
        with ui.div(class_='app-dialog'):
            @render.ui
            @print_func_name
            def renderView():
                match view.get():
                    case 'login':
                        return mod_login(id=getUIID('login'), config_app=config_app, changeView=changeView, changeLoginStatus=changeLoginStatus)
                    case 'create_account':
                        return mod_create_account(id=getUIID('create_account'), config_app=config_app, changeView=changeView)
                    case 'forgot_password':
                        return mod_forgot_password(id=getUIID('forgot_password'), changeView=changeView)
                    case _:
                        return mod_login(id=getUIID('login'), config_app=config_app, changeView=changeView, changeLoginStatus=changeLoginStatus)