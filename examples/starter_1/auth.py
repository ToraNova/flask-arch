import jwt
from flask import current_app

from flask_arch.builtins import PasswordAuth
from flask_arch.exceptions import UserError
from flask_arch.utils import parse_boolean

class MyAuth(PasswordAuth):

    @classmethod
    def parse_auth_data(cls, rp):
        identifier = rp.form[cls.userid] # based on what 'userid' is, in this case it's email
        supplied_auth_data = rp.form['password']
        return identifier, supplied_auth_data

    @classmethod
    def parse_reset_data(cls, rp):
        # this is just one way, alternatively, jd['email'] can also be used
        # the function is required for the user_manager to 'select' the right user
        # to perform password reset
        jd = jwt.decode(rp.form['jwt'], options={"verify_signature": False})
        identifier = jd[cls.userid]
        return identifier

    def reset(self, rp):
        # use the user's authentication data as the key to the jwt,
        # this effectively allows one-time password resets per password
        try:
            jd = jwt.decode(rp.form['jwt'], self.authd, algorithms=["HS256"])
        except Exception as e:
            raise UserError(401, 'invalid token')
        if jd[self.userid] != self.get_id():
            # we should never reach here
            raise UserError(401, 'identifier do not match')
        if rp.form['password_new'] != rp.form['password_confirm']:
            raise UserError(400, 'password do not match')

        self.set_auth_data(rp.form['password_confirm'])
