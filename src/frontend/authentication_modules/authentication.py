from shiny import reactive
from shiny.express import module, ui, render
from .login import mod_login
from .create_account import mod_create_account
from .forgot_password import mod_forgot_password

# -----------------------------------------------------------------------
@module
def mod_authentication(input, output, session, config_app, changeLoginStatus):

    view = reactive.value('login')

    def changeView(value):
        view.set(value)

    @reactive.effect
    def loadViews():
        global login_view, create_account_view, forgot_password_view
        login_view = mod_login(id='login', config_app=config_app, changeView=changeView, changeLoginStatus=changeLoginStatus)
        create_account_view = mod_create_account(id='create_account', config_app=config_app, changeView=changeView)
        forgot_password_view = mod_forgot_password(id='forgot_password', changeView=changeView)

    with ui.hold() as content:
        with ui.div(class_='app-dialog-container'):
            with ui.div(class_='app-dialog'):
                @render.ui
                def showView():
                    match view.get():
                        case 'login':
                            return login_view
                        case 'create_account':
                            return create_account_view
                        case 'forgot_password':
                            return forgot_password_view
                        case _:
                            return login_view

    return content