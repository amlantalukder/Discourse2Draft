from shiny import reactive
from shiny.express import module, ui
from ..db import selectFromDB, insertIntoDB, encryptPassword
from utils import print_func_name
from datetime import datetime

# -----------------------------------------------------------------------
@module
def mod_create_account(input, output, session, config_app, changeView):
    
    with ui.hold() as content:
        with ui.div(class_='row'):
            ui.h5("Create account")
        ui.tags.hr()
        with ui.div(class_='d-flex flex-column p-3 gap-2'):
            with ui.div(class_='row gap-2'):
                ui.input_text('text_first_name', 'First name')
                ui.input_text('text_last_name', 'Last name')
            with ui.div(class_='row'):
                ui.input_text('text_email', 'Email')
            with ui.div(class_='row gap-2'):
                ui.input_password('text_password', 'Password')
                ui.input_password('text_confirm_password', 'Confirm password')
            with ui.div(class_='row justify-content-between'):
                with ui.div(class_='col-auto'):
                    ui.input_action_button('btn_show_login', 'Login')
                with ui.div(class_='col-auto'):
                    ui.input_action_button('btn_create_account', 'Create account')

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_show_login)
    @print_func_name
    def showLogin():
        changeView("login")

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_create_account)
    @print_func_name
    def createAccount():
    
        first_name = input.text_first_name()
        last_name = input.text_last_name()
        email = input.text_email()
        password = input.text_password()
        confirm_password = input.text_confirm_password()

        records = selectFromDB(table_name='credentials', field_names=['email'], field_values=[[email]])

        if not records.empty:
            ui.notification_show('The email address already exists in database, please login with this email address or try to create account with another email address.', type='error')
            return
        
        if password != confirm_password:
            ui.notification_show('Passwords do not match. Please try again.', type='error')
            return
        
        current_time = datetime.now()

        insertIntoDB(table_name='credentials', 
                     field_names=['email', 'first_name', 'last_name', 'password', 'update_date'], 
                     field_values=[[email], [first_name], [last_name], [encryptPassword(password)], current_time])
        insertIntoDB(table_name='settings', 
                     field_names=['email', 'session', 'llm', 'temperature', 'instructions', 'update_date'], 
                     field_values=[[email], [config_app.session_id], [config_app.llm], [config_app.temperature], [config_app.instructions], [current_time]])

        ui.notification_show('Account created.', type='message')

        changeView("login")

    return content