from werkzeug.security import generate_password_hash, check_password_hash

from .. import exceptions

class BaseAuth:
    def auth(self, supplied_auth_data):
        if self.authd is None:
            return False
        return self.check_auth_data(supplied_auth_data)

    @classmethod
    def parse_auth_data(cls, data):
        '''
        this function should return an identifier (to create the user object) and a supplied_auth_data
        the supplied_auth_data is used in the auth(self, supplied_auth_data) method
        '''
        raise NotImplementedError(f'parse_auth_data callback on {cls.__name__} not implemented.')

    def check_auth_data(self, supplied_auth_data):
        '''
        perform authentication on user on the supplied_auth_data
        the supplied_auth_data is parsed by the parse_auth_data(cls, data) method
        '''
        raise NotImplementedError(f'check_auth_data callback on {self.__class__.__name__} not implemented.')

    def set_auth_data(self, supplied_auth_data):
        '''
        sets up the authentication data (self.authd) from the supplied auth data
        this should be called when update/create on user object (if authd is changed)
        '''
        raise NotImplementedError(f'set_auth_data callback on {self.__class__.__name__} not implemented.')

    def parse_reset_data(cls, data):
        '''
        this is used for something like password resets
        return an identifier
        '''
        raise NotImplementedError(f'parse_reset_data callback on {cls.__name__} not implemented.')

    def reset(self, data):
        '''
        this is for the user to reset
        '''
        raise NotImplementedError(f'reset callback on {self.__cls__.__name__} not implemented.')

class PasswordAuth(BaseAuth):

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
    def create(cls, data):
        if data['password'] != data['password_confirm']:
            raise exceptions.UserError('password do not match', 400)
        nu = cls(data['username'], data['password'])
        return nu

    def update(self, data):
        if data.get('password_new'):
            if not self.auth(data['password_old']):
                raise exceptions.UserError('invalid old password', 401)

            if data['password_new'] != data['password_confirm']:
                raise exceptions.UserError('new password do not match', 400)
            self.set_auth_data(data['password_confirm'])

    def delete(self, data):
        if not self.auth(data['password']):
            raise exceptions.UserError('invalid password', 401)
        # do something here
        pass
