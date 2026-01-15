from shiny import reactive
from shiny.express import module, ui
from utils import print_func_name
import smtplib

# -----------------------------------------------------------------------
@module
def mod_forgot_password(input, output, session, changeView):

    with ui.hold() as content:
        with ui.div(class_='row'):
            ui.h5("Forgot Password")
        ui.tags.hr(),
        with ui.div(class_='d-flex flex-column p-3 gap-2'):
            with ui.div(class_='row'):
                ui.input_text('textemail', 'Email')
            with ui.div(class_='row justify-content-between'):
                with ui.div(class_='col-auto'):
                    ui.input_action_button('btn_send_code', 'Send Code')
                with ui.div(class_='col-auto'):
                    ui.input_action_button('btn_show_login', 'Back to Login')

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_send_code)
    @print_func_name
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
        msg['To'] = input.textemail()

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()

    # -----------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_show_login)
    @print_func_name
    def showLogin():
        changeView('login')

    return content