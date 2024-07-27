# Need rework with cryptography, dont use it! Simplify it, using "uuid"
import datetime as date
import logging
import uuid
from functions import dynamo_db as db
from functions import ses_sender as ses

logger = logging.getLogger()
RETRY_ATTEMPT = 3
LOGIN_TIME_LIMIT = 300    # seconds
SESSION_TIME_LIMIT = 1800    # seconds


class Authenticator:
    def __init__(self):
        self.time_now = date.datetime.now()
        self.isAuthorized = False
    
    def start(self,object):
        # human_time = self.time_now.strftime('%y%m%dT%H%M%SZ')
        epoch_time = self.time_now.timestamp()
        new_login_id = ''.join(object,epoch_time)
        new_token = str(uuid.uuid4())
        params = {
                'login_id': {'S': new_login_id},
                'message_id': {'N': int(object)},
                'token': {'S': new_token},
                'timestamp': {'N': int(epoch_time)},
                'sessionActive': {'BOOL': self.isAuthorized}
        }

        db.put_data(params)
        ses.send_mail(new_token)
        logger.info("Login info successfully sent!")

        return None
    
    def login(self,object):
        try:
            uuid.UUID(object['token'])
            if self.login_active(object):
                return "Login successful!"
            else: 
                return "No active session matched, please login again."
        except ValueError:
            raise "This is not a token, I will ignore it."
        

    def login_active(self,object):
        time_range = {
            'min_time': int(self.time_now) - LOGIN_TIME_LIMIT,  # Set minimum time to find oldest time when /login send
            'max_time': int(self.time_now)
        }
        login_list = db.query_data(time_range)

        # try find a matching timestamp
        for session in login_list:
            if object['token'] == session['token']['S']:
                session_id = session['login_id']['S']
                self.isAuthorized = True
                params = {
                            'login_id': {'S': session_id},
                            'message_id': {'N': int(object['msg_id'])},
                            'sessionActive': {'BOOL': self.isAuthorized}
                }
                db.put_data(params)
                return True
            else:
                continue
        
        return False

    def isActive(self,object):
        test_id = int(object) - 2   # Refering to message_id from last sent by user.
        time_range = {
            'min_time': int(self.time_now) - SESSION_TIME_LIMIT,  # Session time should last only for 30 minutes
            'max_time': int(self.time_now)
        }
        session_list = db.query_data(time_range)
        for session in session_list:
            if test_id == session['message_id']['N']:
                session_id = session['login_id']['S']
                if session['sessionActive']:
                    params = {
                            'login_id': {'S': session_id},
                            'message_id': {'N': int(object)}
                    }
                    db.put_data(params) # Update the latest id for next command
                    return True
                else:
                    return False
            else:
                continue
        return False
    
    def revoke_session(self,object):
        test_id = int(object) - 2   # Refering to message_id from last sent by user.
        time_range = {
            'min_time': int(self.time_now) - SESSION_TIME_LIMIT,  # Session time should last only for 30 minutes
            'max_time': int(self.time_now)
        }
        try:
            session_list = db.query_data(time_range)
            for session in session_list:
                if test_id == session['message_id']['N']:
                    session_id = session['login_id']['S']
                    if session['sessionActive']:
                        self.isAuthorized = False
                        params = {
                                'login_id': {'S': session_id},
                                'message_id': {'N': int(object)},
                                'sessionActive': {'BOOL': self.isAuthorized}
                        }
                        db.put_data(params) # Update the latest id for next command
                        logger.info("Session revoked!")
                        return("Session revoked!")
        except Exception as e:
            return f"Error on revoke: {e}"

    

