class Auth:
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

class AuthManager:

    def select_user(self, userid):
        raise NotImplementedError(f'select_user method on {self.__class__.__name__} not implemented.')

    def parse_login(self, data):
        id, ad = self.content_class.parse_auth_data(data)
        return id, ad

    def parse_reset(self, data):
        id = self.content_class.parse_reset_data(data)
        return id

    def register(self, data):
        nu = self.content_class.register(data)
        return nu
