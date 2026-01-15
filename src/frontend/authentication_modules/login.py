from shiny import reactive
from shiny.express import module, ui
from ...backend.db import selectFromDB, insertIntoDB, encryptPassword
from .utils import validateField, FieldType
from utils import print_func_name
from datetime import datetime
import asyncio

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
                #with ui.div(class_='col-auto'):
                #    ui.input_action_button('btn_login_google', 'Login with Google')

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_login)
    @print_func_name
    def login():

        email = input.text_email()
        password = input.text_password()

        success, reason = validateField('Email', email, FieldType.EMAIL)
        if not success:
            ui.notification_show(reason, type='error')
            return

        records = selectFromDB(table_name='credentials', field_names=['email'], field_values=[[email]])

        if records.empty:
            ui.notification_show('The email address does not exist.', type='error')
            return
        
        if records['password'].iloc[0] != encryptPassword(password):
            ui.notification_show('The password is not correct.', type='error')
            return

        config_app.email = email
        loop = asyncio.get_event_loop()
        loop.create_task(session.send_custom_message('auth_key', {'email': config_app.email}))

        changeLoginStatus('logged_in')

        ui.notification_show('Login successful.', type='message')

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_create_account)
    @print_func_name
    def showCreateAccount():
        changeView("create_account")

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_forgot_password)
    @print_func_name
    def showForgotPassword():
        changeView("forgot_password")

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_guest)
    @print_func_name
    def guestLogin():

        current_time = datetime.now()

        insertIntoDB(table_name='settings', 
                     field_names=['email', 'session', 'llm', 'temperature', 'instructions', 'create_date', 'update_date'], 
                     field_values=[[config_app.email], [config_app.session_id], [config_app.llm], [config_app.temperature], [config_app.instructions], [current_time], [current_time]])

        changeLoginStatus('guest')

    def getGoogleAuthURL():
        import google_auth_oauthlib.flow

        # Required, call the from_client_secrets_file method to retrieve the client ID from a
        # client_secret.json file. The client ID (from that file) and access scopes are required. (You can
        # also use the from_client_config method, which passes the client configuration as it originally
        # appeared in a client secrets file but doesn't access the file itself.)
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('google_auth.json', scopes=['openid'])

        # Required, indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required. The value must exactly
        # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
        # configured in the API Console. If this value doesn't match an authorized URI,
        # you will get a 'redirect_uri_mismatch' error.
        flow.redirect_uri = 'http://127.0.0.1:8222/'

        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Recommended, enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Optional, enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true',
            # Optional, if your application knows which user is trying to authenticate, it can use this
            # parameter to provide a hint to the Google Authentication Server.
            login_hint='amlanaccount@gmail.com',
            # Optional, set prompt to 'consent' will prompt the user for consent
            prompt='consent')
        
        return authorization_url

    @reactive.effect
    @reactive.event(input.btn_login_google)
    @print_func_name
    async def loginWithGoogle():
        authorization_url = getGoogleAuthURL()
        #ui.HTML(f'<a href="{authorization_url}" target="_blank">Visit Posit</a>')
        target_url = "https://www.posit.co/" # Dynamic URL can be generated here
        await session.send_custom_message("redirect", {"url": authorization_url})

    return content
