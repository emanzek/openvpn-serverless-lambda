import string
import random
import datetime as date
import logging
from cryptography.fernet import Fernet
from functions import dynamo_db as db
from functions import ses_sender as ses

logger = logging.getLogger()
TOKEN_LEN = 32


class Authenticator:
    def __init__(self):
        self.time_now = date.datetime.now()
        self.isAuthorized = False
    
    def start(self,object):
        epoch_time = self.time_now.timestamp()
        human_time = self.time_now.strftime('%y%m%dT%H%M%SZ')
        new_login_id = ''.join(epoch_time,object)
        new_token = self.gen_token(TOKEN_LEN)
        new_sessionToken = self.gen_sessionKey()
        params = {
                'login_id': {'S': new_login_id},
                'token': {'S': new_token},
                'timeStamp': {'S': epoch_time},
                'sessionActive': {'BOOL': self.isAuthorized},
                'sessionKey': {'B': new_sessionToken}
        }

        db.put_data(params)
        encrypted_token = self.encrypt_message(new_token)

        credentials = '-'.join(new_login_id,encrypted_token)
        ses.send_mail(credentials)
        logger.info("Login Info successfully sent!")

        return None
    
    def login(self,object):
        if len(object) > TOKEN_LEN:
            parse_cred = object.split('-')
            params = {
                'Key': {
                    'login_id': parse_cred[0]
                }
            }

            login_session = db.get_data(params)
            if login_session != None:
                try:
                    test_token = login_session['token']
                    encrypt_key = login_session['sessionKey']
                    decrypted_token = self.decrypt_message(parse_cred[1],encrypt_key)
                    if decrypted_token == test_token:
                        self.isAuthorized = True
                        params = {
                            'login_id': {'S': parse_cred[0]},
                            'sessionActive': {'BOOL': self.isAuthorized}
                        }
                        db.put_data(params)
                    else:
                        raise Exception("Token unmatched!")
                except Exception as e:
                    return "Key unmatched {}".format(e) 
            else:
                return "No session found."
        else:
            raise Exception('This is not credentials.')

    def isActive():
        
        params = {
            'Key': {
                'login_id': object
            }
        }
        message = "Your activity still active. Able to proceed with another command"
        session = db.get_data(params)
        state = session['sessionActive']
        return state
    
    def revokeToken(data):
        return "Your activity has been terminated! Please login again to use other command."
    
    def gen_token(token_len):
        char = string.ascii_letters + string.digits + string.punctuation
        token = ''.join(random.choice(char) for i in range(token_len))
        return token
    
    def gen_sessionKey():
        key = Fernet.generate_key()
        return key

    def encrypt_message(data,key):
        fernet = Fernet(key)
        encrypted_message = fernet.encrypt(data.encode())
        return encrypted_message
    
    def decrypt_message(data,key):
        fernet = Fernet(key)
        decrypted_message = fernet.decrypt(data).decode()
        return decrypted_message

    

