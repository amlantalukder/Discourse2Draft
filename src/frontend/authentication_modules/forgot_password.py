from shiny import reactive
from shiny.express import module, ui, render
import logging
import uuid
import time
from datetime import datetime
from utils import print_func_name, Config
from .utils import validateField, FieldType
from ...backend.db import selectFromDB, updateDB, encryptPassword

# -----------------------------------------------------------------------
@module
def mod_forgot_password(input, output, session, changeView):

    activation_code = reactive.Value({})
    show_reset_password = reactive.Value(False)

    with ui.hold() as content:
        with ui.div(class_='row'):
            ui.h5("Forgot Password")
        ui.tags.hr(),
        with ui.div(class_='d-flex flex-column p-3 gap-2 justify-content-between'):
            with ui.div(class_='row'):
                ui.input_text('text_email', 'Email')
            @render.express
            def renderActivationCode():
                if show_reset_password.get():
                    with ui.div(class_='row gap-2'):
                        ui.input_password('text_password', 'Password')
                        ui.input_password('text_confirm_password', 'Confirm password')
                        ui.help_text("Password must contain at least 8 characters, with at least one letter, one number, and one special character (!_@#$%^&*(),.?\":{{}}|<>).")
                    with ui.div(class_='row justify-content-between mt-3'):
                        with ui.div(class_='col-auto'):
                            ui.input_action_button('btn_reset_password', 'Reset Password')
                        with ui.div(class_='col-auto'):
                            ui.input_action_button('btn_show_login', 'Back to Login')
                    return
                
                if not activation_code.get(): 
                    with ui.div(class_='row justify-content-between'):
                        with ui.div(class_='col-auto'):
                            ui.input_action_button('btn_send_code', 'Send Code')
                        with ui.div(class_='col-auto'):
                            ui.input_action_button('btn_show_login', 'Back to Login')
                    return
                with ui.div(class_='row justify-content-between align-items-end'):
                    with ui.div(class_='col-auto'):
                        ui.input_text('text_activation_code', 'Activation Code', value='')
                    with ui.div(class_='col-auto pb-3'):
                        ui.input_action_button('btn_verify_code', 'Verify Code')
                with ui.div(class_='row justify-content-between'):
                    with ui.div(class_='col-auto'):
                        ui.input_action_button('btn_send_code', 'Resend Code')
                    with ui.div(class_='col-auto'):
                        ui.input_action_button('btn_show_login', 'Back to Login')

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_send_code)
    @print_func_name
    def forgotPasswordSendLink():

        import requests

        def send_simple_message(email, code):
            

            response = requests.post(
                            f"https://api.mailgun.net/v3/{Config.env_config['MAILGUN_DOMAIN']}/messages",
                            auth=("api", Config.env_config['MAILGUN_API_KEY']),
                            data={"from": f"Mailgun Sandbox <postmaster@{Config.env_config['MAILGUN_API_KEY']}>",
                                "to": email,
                                "subject": "Activation code for Discourse2Draft",
                                "text": f"Activation code: {code}"})
            
            if response.status_code != 200:
                raise Exception(f"{response.status_code} {response.text}")

        email = input.text_email()

        records = selectFromDB(table_name='credentials', field_names=['email'], field_values=[[email]])

        if records.empty:
            ui.notification_show(('Email address does not exist in database.' 
                                 'Please create an account with this email address or '
                                 'try again with a different email address.'), type='error', duration=10)
            return
        
        if not email:
            ui.notification_show('Please enter your email', type='error')
            return
        
        code = uuid.uuid4().hex[:6].upper()
        
        try:
            send_simple_message(email=email, code=code)
            ui.notification_show('Code sent successfully', type='message')
            activation_code.set({'code': code, 'email': email, 'timestamp': time.time()})
        except Exception as exp:
            logging.error(f'Error sending activation code to user {email}: {str(exp)}') 
            ui.notification_show('Error sending code', type='error')

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_verify_code)
    @print_func_name
    def verifyCode():

        if not activation_code.get():
            ui.notification_show('Please request an activation code first', type='error')
            return

        code = input.text_activation_code()
        if code != activation_code.get().get('code'):
            if time.time() - activation_code.get().get('timestamp', 0) > 15 * 60: # 15 minutes expiration
                ui.notification_show('Activation code expired. Please request a new one.', type='error')
                activation_code.set({})
                return 
            
            ui.notification_show('Invalid activation code', type='error')
            return
        
        show_reset_password.set(True)

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_reset_password)
    @print_func_name
    def resetPassword():
    
        password = input.text_password()
        confirm_password = input.text_confirm_password()

        for field_name, field_value, field_type in zip(['Password', 'Confirm password'],
                                                       [password, confirm_password],
                                                       [FieldType.PASSWORD.value, FieldType.PASSWORD.value]):
            success, reason = validateField(field_name, field_value, field_type)
            if not success:
                ui.notification_show(reason, type='error')
                return
            
        if password != confirm_password:
            ui.notification_show('Passwords do not match. Please try again.', type='error')
            return
        
        current_time = datetime.now()

        updateDB(table_name='credentials', 
                 update_fields=['password', 'update_date'], 
                 update_values=[encryptPassword(password), current_time],
                 select_fields=['email'],
                 select_values=[[activation_code.get().get('email')]]
        )

        ui.notification_show('Password reset successfully. Please log in with your new password.', type='message', duration=10)
        
        activation_code.set({})
        show_reset_password.set(False)

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_show_login)
    @print_func_name
    def showLogin():
        changeView('login')

    return content