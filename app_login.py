from shiny import ui as core_ui, reactive
from shiny.express import module, ui
import hashlib
from db import selectFromDB, insertIntoDB
import smtplib

# -----------------------------------------------------------------------
def showDialog(ui_content):

    m = ui.modal(
        ui_content,
        title="",
        easy_close=True,
        footer=None,
        size='m'
    )

    ui.modal_show(m)

@module
def mod_login(input, output, session, callback_fn, config_app):

    # -----------------------------------------------------------------------
    login_content = core_ui.div(
        core_ui.div(
            core_ui.h5("Login"),
            class_='row'
        ),
        core_ui.tags.hr(),
        core_ui.div(
            core_ui.div(
                core_ui.input_text('text_email_li', 'Email'),
                core_ui.input_password('text_password_li', 'Password'),
                class_='row'
            ),
            core_ui.div(
                core_ui.div(
                    core_ui.input_action_button('btn_login_li', 'Login'),
                    class_='col-auto'
                ),
                core_ui.div(
                    core_ui.input_action_button('btn_create_account_li', 'Create Account'),
                    class_='col-auto'
                ),
                core_ui.div(
                    core_ui.input_action_button('btn_forgot_password_li', 'Forgot Password'),
                    class_='col-auto'
                ),
                class_='row justify-content-between'
            ),
            class_='d-flex flex-column p-3 gap-2'
        )
    )

    # -----------------------------------------------------------------------
    create_account_content = core_ui.div(
        core_ui.div(
            core_ui.h5("Create account"),
            class_='row'
        ),
        core_ui.tags.hr(),
        core_ui.div(
            core_ui.div(
                core_ui.input_text('text_first_name_ca', 'First name'),
                core_ui.input_text('text_last_name_ca', 'Last name'),
                class_='row'
            ),
            core_ui.div(
                core_ui.input_text('text_email_ca', 'Email'),
                core_ui.input_password('text_password_ca', 'Password'),
                core_ui.input_password('text_confirm_password_ca', 'Confirm password'),
                class_='row'
            ),
            core_ui.div(
                core_ui.div(
                    core_ui.input_action_button('btn_show_login_ca', 'Login'),
                    class_='col-auto'
                ),
                core_ui.div(
                    core_ui.input_action_button('btn_create_account_ca', 'Create account'),
                    class_='col-auto'
                ),
                class_='row justify-content-center'
            ),
            class_='d-flex flex-column p-3 gap-2'
        )
    )

    # -----------------------------------------------------------------------
    forgot_password_content = core_ui.div(
        core_ui.div(
            core_ui.h5("Forgot Password"),
            class_='row'
        ),
        core_ui.tags.hr(),
        core_ui.div(
            core_ui.div(
                core_ui.input_text('txt_email_fp', 'Email'),
                class_='row'
            ),
            core_ui.div(
                core_ui.div(
                    core_ui.input_action_button('btn_show_login_fp', 'Login'),
                    class_='col-auto'
                ),
                core_ui.div(
                    core_ui.input_action_button('btn_send_code_fp', 'Send Code'),
                    class_='col-auto'
                ),
                class_='row justify-content-center'
            ),
            class_='d-flex flex-column p-3 gap-2'
        )
    )

    # -----------------------------------------------------------------------
    def encryptPassword(password):

        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        # Convert the password to bytes and hash it
        hash_object.update(password.encode())
        # Get the hex digest of the hash
        return hash_object.hexdigest()

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_login_li, ignore_init=True)
    def login():

        email = input.text_email_li()
        password = input.text_password_li()

        records = selectFromDB(table_name='credentials', field_names=['Email'], field_values=[[email]])

        if records.empty:
            ui.notification_show('The email address does not exist.', type='error')
            return
        
        if records['Password'].iloc[0] != encryptPassword(password):
            ui.notification_show('The password is not correct.', type='error')
            return
        print('\n\nwith login...\n\n')
        ui.modal_remove()
        ui.notification_show('Login successful.', type='message')

        config_app.email = email

        callback_fn()

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_create_account_li, ignore_init=True)
    def showCreateAccount():
        ui.modal_remove()
        showDialog(create_account_content)

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_forgot_password_li, ignore_init=True)
    def showForgotPassword():
        ui.modal_remove()
        showDialog(forgot_password_content)

    # -----------------------------------------------------------------------
    # Create account
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_show_login_ca, ignore_init=True)
    def showLogin():
        ui.modal_remove()
        showDialog(login_content)

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_create_account_ca, ignore_init=True)
    def createAccount():
    
        first_name = input.text_first_name_ca()
        last_name = input.text_last_name_ca()
        email = input.text_email_ca()
        password = input.text_password_ca()
        confirm_password = input.text_confirm_password_ca()

        records = selectFromDB(table_name='credentials', field_names=['Email'], field_values=[[email]])

        if not records.empty:
            ui.notification_show('The email address already exists in database, please login with this email address or try to create account with another email address.', type='error')
            return
        
        if password != confirm_password:
            ui.notification_show('Passwords do not match. Please try again.', type='error')
            return
        
        insertIntoDB(table_name='credentials', field_names=['Email', 'First Name', 'Last Name', 'Password'], field_values=[[email], [first_name], [last_name], [encryptPassword(password)]])
        insertIntoDB(table_name='settings', field_names=['Email', 'LLM', 'Temperature', 'Instructions'], field_values=[[email], [config_app.llm], [config_app.temperature], [config_app.instructions]])

        ui.notification_show('Account created.', type='message')

        ui.modal_remove()
        showDialog(login_content)

    # -----------------------------------------------------------------------
    # Forgot password
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_send_code_fp, ignore_init=True)
    def forgotPasswordSendLink():
        ui.notification_show('Not implemented yet', type='message')
        return
        
        # Import the email modules we'll need
        from email.mime.text import MIMEText

        msg = MIMEText(
            f'''# Your verification code:
            123456                                    
            '''
        )

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = 'AI Word Processor: password reset'
        msg['From'] = 'amlanaccount@gmail.com'
        msg['To'] = input.txt_email_fp()

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_show_login_fp, ignore_init=True)
    def showLogin():
        ui.modal_remove()
        showDialog(login_content)

    return login_content
