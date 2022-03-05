from .base import User

from ....auth.base import Auth, AuthManager
from ....cms.volatile.procmem import ContentManager

class UserManager(AuthManager, ContentManager):

    def __init__(self, auth_class, user_class=User):
        if not issubclass(auth_class, Auth):
            raise TypeError(f'{auth_class} should be a subclass of {Auth}.')
        if not issubclass(user_class, User):
            raise TypeError(f'{user_class} should be a subclass of {User}.')

        class AuthUser(auth_class, user_class):
            pass

        self.content_class = AuthUser
        self.data = {}

    def select_user(self, userid):
        return self.select_one(userid)
