class Auth:
    def auth(self, supplied_auth_data):
        '''
        perform authentication on user on the supplied_auth_data
        the supplied_auth_data is parsed by the parse_auth_data(cls, data) method
        '''
        raise NotImplementedError(f'check_auth_data on {self.__class__.__name__} not implemented.')

    def set_auth_data(self, supplied_auth_data):
        '''
        sets up the authentication data (self.authd) from the supplied auth data
        this should be called when update/create on user object (if authd is changed)
        '''
        raise NotImplementedError(f'set_auth_data on {self.__class__.__name__} not implemented.')

    def reset(self, request):
        '''
        this is for the user to reset
        '''
        raise NotImplementedError(f'reset on {self.__cls__.__name__} not implemented.')

    @classmethod
    def parse_auth_data(cls, request):
        '''
        this function should return an identifier (to create the user object) and a supplied_auth_data
        the supplied_auth_data is used in the auth(self, supplied_auth_data) method
        '''
        raise NotImplementedError(f'parse_auth_data on {cls.__name__} not implemented.')

    @classmethod
    def parse_reset_data(cls, request):
        '''
        this is used for something like password resets
        return an identifier
        '''
        raise NotImplementedError(f'parse_reset_data on {cls.__name__} not implemented.')


class AuthManager:

    def prepare_login(self, rp):
        id, d = self.Content.parse_auth_data(rp)
        u = self.select_user(id)
        return u, d

    def prepare_reset(self, rp):
        id = self.Content.parse_reset_data(rp)
        u = self.select_user(id)
        return u

    def select_user(self, userid):
        raise NotImplementedError(f'select_user method on {self.__class__.__name__} not implemented.')
