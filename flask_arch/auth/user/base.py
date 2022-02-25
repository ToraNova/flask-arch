class User:
    '''
    ancestor of all authenticated users
    default attributes: is_authenticated, is_active, is_anonymous, userid (key), id, authd
    '''
    is_anonymous = False
    is_authenticated = False

    __contentname__ = "auth_user"

    # user identifier key. (e.g., if set to id, means user.id will identify the user)
    userid = 'id'

    def __init__(self, identifier, authd):
        setattr(self, self.userid, identifier)
        self.set_auth_data(authd)
        self.is_active = True

    def get_id(self):
        if self.is_anonymous:
            return None
        else:
            return getattr(self, self.userid)

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

    @classmethod
    def populate_template_data(cls):
        # no template data to populate, use current_user to obtain user info
        pass
