import requests
from src.utils import Config

def testEmailService():

    ## Test sending activation code for authentication
    email = 'dummy@email.com'
    response = requests.post(
                    f"https://api.mailgun.net/v3/{Config.env_config['MAILGUN_DOMAIN']}/messages",
                    auth=("api", Config.env_config['MAILGUN_API_KEY']),
                    data={"from": f"Mailgun Sandbox <postmaster@{Config.env_config['MAILGUN_API_KEY']}>",
                        "to": email,
                        "subject": "Activation code for Discourse2Draft",
                        "text": f"Activation code: 123456"}
                )
    print(response.status_code, response.text)


