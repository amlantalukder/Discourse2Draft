from shiny import reactive
from shiny.express import module, ui
from db import selectFromDB, encryptPassword

# -----------------------------------------------------------------------
@module
def mod_login(input, output, session, config_app, changeView, changeLoginStatus):

    with ui.hold() as content:
        with ui.div(class_='row'):
            with ui.h5():
                "Login"
        ui.tags.hr(),
        with ui.div(class_='d-flex flex-column p-3 gap-2'):
            with ui.div(class_='row'):
                ui.input_text('text_email', 'Email')
            with ui.div(class_='row'):
                ui.input_password('text_password', 'Password')
            with ui.div(class_='row justify-content-between'):
                with ui.div(class_='col-auto'):
                    ui.input_action_button('btn_login', 'Login'),
                with ui.div(class_='col-auto'):
                    ui.input_action_button('btn_create_account', 'Create Account')
                with ui.div(class_='col-auto'):
                    ui.input_action_button('btn_forgot_password', 'Forgot Password')
            with ui.div(class_='row justify-content-center mt-2'):
                with ui.div(class_='col-auto'):
                    ui.input_action_link('btn_guest', 'Continue Without Login')

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_login)
    def login():

        email = input.text_email()
        password = input.text_password()

        records = selectFromDB(table_name='credentials', field_names=['email'], field_values=[[email]])

        if records.empty:
            ui.notification_show('The email address does not exist.', type='error')
            return
        
        if records['password'].iloc[0] != encryptPassword(password):
            ui.notification_show('The password is not correct.', type='error')
            return

        config_app.email = email

        changeLoginStatus('logged_in')

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_create_account)
    def showCreateAccount():
        changeView("create_account")

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_forgot_password)
    def showForgotPassword():
        changeView("forgot_password")

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_guest)
    def continueWithLogin():
        changeLoginStatus('guest')

    return content
