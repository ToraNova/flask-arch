from werkzeug.security import generate_password_hash, check_password_hash

from .. import exceptions
from ..auth import base

class Auth(base.Auth):

    @classmethod
    def parse_auth_data(cls, rp):
        username = rp.form['username']
        supplied_auth_data = rp.form['password']
        return username, supplied_auth_data

    def auth(self, supplied_auth_data):
        return check_password_hash(self.authd, supplied_auth_data)

    def set_auth_data(self, supplied_auth_data):
        method = 'pbkdf2:sha512'
        saltlen = 16
        self.authd = generate_password_hash(supplied_auth_data, method=method, salt_length=saltlen)

    def __init__(self, rp, actor):
        super().__init__(rp, actor)

        if rp.form.get('password_confirm'):
            if rp.form['password'] != rp.form['password_confirm']:
                raise exceptions.UserError(400, 'password do not match')
        self.set_auth_data(rp.form['password'])

    def modify(self, rp, actor):
        super().modify(rp, actor)
        if actor == self:
            # user is updating their own information
            if rp.form.get('password_new'):
                if not self.auth(rp.form['password_old']):
                    raise exceptions.UserError(401, 'invalid old password')

                if rp.form.get('password_confirm'):
                    if rp.form['password_new'] != rp.form['password_confirm']:
                        raise exceptions.UserError(400, 'new password do not match')
                self.set_auth_data(rp.form['password_confirm'])

    def deinit(self, rp, actor):

        if actor == self:
            # user is deleting themselves
            if not self.auth(rp.form['password']):
                raise exceptions.UserError(401, 'invalid password')
