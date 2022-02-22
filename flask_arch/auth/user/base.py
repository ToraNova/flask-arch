from flask_arch.cms import BaseContentMixin

class BaseUserMixin(BaseContentMixin):
    '''basic user without any means of authentication'''

    is_authenticated = False # default to be false, unless flask_login sets it true
    is_active = False # default to be active
    is_anonymous = False
    userid = 'id'

    def get_id(self):
        if self.is_anonymous:
            return None
        else:
            return getattr(self, self.userid)

    @property
    def id(self):
        return self.get_id()

    @classmethod
    def parse_auth_data(cls, data):
        '''
        this function should return an identifier (to create the user object) and a supplied_auth_data
        the supplied_auth_data is used in the auth(self, supplied_auth_data) method
        '''
        raise NotImplementedError(f'parse_auth_data callback on {cls.__name__} not implemented')

    def auth(self, supplied_auth_data):
        '''
        perform authentication on user on the supplied_auth_data
        the supplied_auth_data is parsed by the parse_auth_data(cls, data) method
        '''
        raise NotImplementedError(f'auth callback on {self.__class__.__name__} not implemented')

    @classmethod
    def populate_template_data(cls):
        # no template data to populate, use current_user to obtain user info
        pass
