# basic user class to work with flask-login

from werkzeug.security import generate_password_hash, check_password_hash

class Basic:
    '''A basic user authentication account following flask-login'''

    def __init__(self, name, password):
        self.set_password(password)
        self.name = name
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.name
        #return str(self.id)

    def set_password(self, password, method ='pbkdf2:sha512', saltlen = 16 ):
        self.passhash=generate_password_hash(password, method=method, salt_length=saltlen)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)
