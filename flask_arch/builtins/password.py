from werkzeug.security import generate_password_hash, check_password_hash

from .. import exceptions
from ..auth import base

class Auth(base.Auth):

    def __init__(self, username, password):
        super().__init__(username)
        self.set_auth_data(password)

    @classmethod
    def parse_auth_data(cls, data):
        username = data['username']
        supplied_auth_data = data['password']
        return username, supplied_auth_data

    def check_auth_data(self, supplied_auth_data):
        return check_password_hash(self.authd, supplied_auth_data)

    def set_auth_data(self, supplied_auth_data):
        method = 'pbkdf2:sha512'
        saltlen = 16
        self.authd = generate_password_hash(supplied_auth_data, method=method, salt_length=saltlen)

    @classmethod
    def register(cls, data):
        # user register themself
        if data['password'] != data['password_confirm']:
            raise exceptions.UserError('password do not match', 400)
        nu = cls(data['username'], data['password'])
        return nu

    def renew(self, data):
        # user renew own account
        if data.get('password_new'):
            if not self.auth(data['password_old']):
                raise exceptions.UserError('invalid old password', 401)

            if data['password_new'] != data['password_confirm']:
                raise exceptions.UserError('new password do not match', 400)
            self.set_auth_data(data['password_confirm'])

    def remove(self, data):
        # user remove themselves
        if not self.auth(data['password']):
            raise exceptions.UserError('invalid password', 401)
        # do something here
        pass

