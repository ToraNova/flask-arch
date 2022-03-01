from ..cms import BaseContent

class BaseUser(BaseContent):
    '''
    ancestor of all authenticated users
    default attributes: is_authenticated, is_active, is_anonymous, userid (key), id, authd
    '''
    is_anonymous = False
    is_authenticated = False

    __contentname__ = "auth_user"

    # user identifier key. (e.g., if set to id, means user.id will identify the user)
    userid = 'id'

    def __init__(self, identifier):
        setattr(self, self.userid, identifier)
        self.is_active = True

    def get_id(self):
        if self.is_anonymous:
            return None
        else:
            return getattr(self, self.userid)

    @classmethod
    def populate_template_data(cls):
        # no template data to populate, use current_user to obtain user info
        pass

class BaseUserManager:

    def select_user(self, userid):
        raise NotImplementedError(f'select_user method on {self.__class__.__name__} not implemented.')

    def parse_login(self, data):
        id, ad = self.content_class.parse_auth_data(data)
        return id, ad

    def parse_reset(self, data):
        id = self.content_class.parse_reset_data(data)
        return id
