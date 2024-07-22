# TODO: 1. Implement authentication, this need email and db service (DynamoDB, SES)
#       2. Integrate with SNS for cloudformation status
#       3. Organize code function
#       4. Generalize the deployment steps

import json
import requests
import logging
import os
from functions import auth
from functions import ec2_instance as ec2
from functions import s3_files as s3
from functions import dynamo_db as db

logger = logging.getLogger()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_CHAT_ID = os.environ.get('BOT_CHAT_ID')
authentication = auth.Authenticator()

def main(event, context):
    logger.debug("Incoming event object: %s", event)
    request_body = json.loads(event['body'])
    command = request_body['message']['text']
    message_id = request_body['message']['message_id']
    message_date = request_body['message']['date']
    
    match command:
        case '/start':
            logger.info("Bot started")
            send_text("Welcome to OpenVPN-bot! Please use /login to authorized any request.")
        case '/login':
            logger.info("Login started")
            authentication.start(message_id)
            message = "We've sent you a line of token through the email, please submit it in here with session_id to get authorized."
            send_text(message)
        case '/create':
            if authentication.isActive():
                logger.info("Create started")
                send_text("Creating the instance now...")
                try:
                    message = ec2.create()
                except Exception as e:
                    message = "Oops! There's an error, won't do anything for now.\nERROR: {}".format(e)
            else:
                message = "Permission denied!"
            send_text(message)
        case '/destroy':
            if authentication.isActive():    
                logger.info("Destroy started")
                send_text("Terminating...")
                try:
                    message = ec2.destroy()
                except Exception as e:
                    message = "Oops! There's an error, won't do anything for now.\nERROR: {}".format(e)
            else:
                message = "Permission denied!"
            send_text(message)
        case '/help':
            message = "Here's some list you could try with:\n /create - Create VPN connection.\n /destroy - Destroy VPN connection.\n /help - List all command."
            send_text(message)
        case '/stop':
            message = "Revoking any access."
            send_text(message)
        case _:
            try:
                message = "This is what u trying to send: {} at {}".format(message_id,message_date)
                send_text(message)
                decrypt_token = authentication.login(command)

            except Exception as e:
                message = "Nope, you can't do that here sir. Please try again."
            logger.info("Different command sent!")
            send_text(message)
    
    body = {
        "message": "Message sent to telegram!",
        "sent": "Hello from Lambda!"
    }

    response = {"statusCode": 200, "body": json.dumps(request_body)}

    return response

def send_text(message):
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(BOT_TOKEN)
    data = {'chat_id': BOT_CHAT_ID}
    params = {
        'parse_mode': 'HTML',
        'text': message
    }
    
    sender = requests.get(url,data=data,params=params)
    
    return sender

def clientUploaded(event, context):
    logger.info("Event object: %s", event)

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key_name = event['Records'][0]['s3']['object']['key']
    filename = key_name.split('/')[1:][0]
    filepath = "/tmp/{}".format(filename)
    s3.get_files(bucket_name,key_name,filepath)

    files = [('document',(filename,open(filepath,'rb'),'application/octet-stream'))]
    url = 'https://api.telegram.org/bot{}/sendDocument'.format(BOT_TOKEN)
    payload = {'chat_id': BOT_CHAT_ID}
    headers = {}
    response = requests.post(url=url,headers=headers,data=payload,files=files)

    return response.status_code