import datetime
from flask_arch import exceptions
from flask_arch.auth.user.base import BaseUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_arch.cms import SQLDeclarativeBase, SQLContentMixin, declared_attr, Column, Integer, String, Boolean, DateTime

class PasswordUserMixin(BaseUserMixin):
    '''usermixin for password-based users'''

    def set_password(self, password, method='pbkdf2:sha512', saltlen=16):
        self.passhash = generate_password_hash(password, method=method, salt_length=saltlen)

    @classmethod
    def create(cls, data):
        if data['password'] != data['password_confirm']:
            raise exceptions.UserError(400, 'password do not match')
        return cls(data['username'], data['password'])

    def update(self, data):
        if data.get('password_new'):
            if not self.auth(data['password_old']):
                raise exceptions.UserError(401, 'invalid old password')

            if data['password_new'] != data['password_confirm']:
                raise exceptions.UserError(400, 'new password do not match')
            self.set_password(data['password_confirm'])

    def delete(self, data):
        if not self.auth(data['password']):
            raise exceptions.UserError(401, 'invalid password')
        # do something here
        pass

    @classmethod
    def parse_auth_data(cls, data):
        # first argument returned is the user identifier
        # second argument returned is the supplied auth_data
        username = data['username']
        supplied_auth_data = data['password']
        return username, supplied_auth_data

    def auth(self, supplied_auth_data):
        # test supplied auth_data, obtained from parse_auth_data
        return check_password_hash(self.passhash, supplied_auth_data)

class PasswordUser(PasswordUserMixin):
    '''a simple password user class'''

    # identify user with 'name' attribute
    userid = 'name'

    def __init__(self, username, password):
        self.set_password(password)
        self.name = username
        self.is_active = True

class SQLPasswordUser(SQLContentMixin, PasswordUserMixin, SQLDeclarativeBase):
    '''password user class for database'''

    __tablename__ = "auth_user"
    # This prevents errors,
    # BUT DO NOT USE UNDER NORMAL CIRCUMSTANCES AS IT MAY INDICATE MULTIPLE DEFINITIONS
    __table_args__ = {'extend_existing': True}
    # identify user with 'name' attribute
    userid = 'name'

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key = True)

    @declared_attr
    def name(cls):
        return Column(String(50),unique=True,nullable=False)

    @declared_attr
    def passhash(cls):
        return Column(String(160),unique=False,nullable=False)

    @declared_attr
    def is_active(cls):
        return Column(Boolean(),nullable=False) #used to disable accounts

    @declared_attr
    def created_on(cls):
        return Column(DateTime()) #date of user account creation

    @declared_attr
    def updated_on(cls):
        return Column(DateTime()) #updated time

    def __init__(self, username, password):
        self.set_password(password)
        self.name = username
        self.is_active = True
        self.created_on = datetime.datetime.now()
        self.updated_on = self.created_on

    def update(self, data):
        super().update(data)
        self.updated_on = datetime.datetime.now()
