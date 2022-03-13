import jwt
from flask import current_app

from flask_arch.builtins import PasswordAuth
from flask_arch.exceptions import UserError
from flask_arch.utils import parse_boolean

class MyAuth(PasswordAuth):

    def __init__(self, email, username, role_id, password):
        super().__init__(email, password)
        self.role_id = role_id
        self.name = username # username is extra, not used to identify the user

    @classmethod
    def parse_auth_data(cls, data):
        email = data['email']
        supplied_auth_data = data['password']
        return email, supplied_auth_data

    @classmethod
    def parse_reset_data(cls, data):
        # this is just one way, alternatively, data['email'] can also be used
        # the function is required for the user_manager to 'select' the right user
        # to perform password reset
        jd = jwt.decode(data['jwt'], options={"verify_signature": False})
        return jd['email']

    def reset(self, data):
        # use the user's authentication data as the key to the jwt,
        # this effectively allows one-time password resets per password
        try:
            jd = jwt.decode(data['jwt'], self.authd, algorithms=["HS256"])
        except Exception as e:
            raise UserError('invalid token', 401)
        if data['password_new'] != data['password_confirm']:
            raise UserError('password do not match', 400)
        if jd['email'] != self.email:
            # we should never reach here
            raise UserError('email do not match', 401)

        self.set_auth_data(data['password_confirm'])

    @classmethod
    def create(cls, data):
        # created by an admin
        if data['password'] != data['password_confirm']:
            raise UserError('password do not match', 400)
        nu = cls(data['email'], data['username'], data['role_id'], data['password'])
        return nu

    @classmethod
    def register(cls, data):
        #self register
        if data['password'] != data['password_confirm']:
            raise UserError('password do not match', 400)
        # jwt is obtained from email verify request
        print(data)
        jd = jwt.decode(data['jwt'], current_app.secret_key, algorithms=["HS256"])
        nu = cls(jd['email'], data['username'], None, data['password'])
        return nu

    def update(self, data):
        self.role_id = data['role_id']

    def delete(self, data):
        pass
