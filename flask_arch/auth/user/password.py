from werkzeug.security import generate_password_hash, check_password_hash

from . import base
from ... import exceptions

class UserMixin:
    '''usermixin for password-based users'''

    @classmethod
    def parse_auth_data(cls, data):
        # first argument returned is the user identifier
        # second argument returned is the supplied auth_data
        username = data['username']
        supplied_auth_data = data['password']
        return username, supplied_auth_data

    def set_auth_data(self, password):
        method = 'pbkdf2:sha512'
        saltlen = 16
        self.authd = generate_password_hash(password, method=method, salt_length=saltlen)

    def check_auth_data(self, supplied_auth_data):
        # test supplied auth_data, obtained from parse_auth_data
        return check_password_hash(self.authd, supplied_auth_data)

    @classmethod
    def create(cls, data, creator=None):
        if data['password'] != data['password_confirm']:
            raise exceptions.UserError(400, 'password do not match')
        nu = cls(data['username'], data['password'])
        if isinstance(creator, base.User):
            nu.owner_id = creator.id
        return nu

    def update(self, data):
        if data.get('password_new'):
            if not self.auth(data['password_old']):
                raise exceptions.UserError(401, 'invalid old password')

            if data['password_new'] != data['password_confirm']:
                raise exceptions.UserError(400, 'new password do not match')
            self.set_auth_data(data['password_confirm'])

    def delete(self, data):
        if not self.auth(data['password']):
            raise exceptions.UserError(401, 'invalid password')
        # do something here
        pass
