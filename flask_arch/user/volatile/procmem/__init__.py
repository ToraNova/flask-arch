from .base import User

from ....auth import BaseAuth
from ....cms.volatile.procmem import ContentManager

class UserManager(ContentManager):

    def __init__(self, auth_class, user_class=User):
        if not issubclass(auth_class, BaseAuth):
            raise TypeError(f'{auth_class} should be a subclass of {BaseAuth}.')
        if not issubclass(user_class, User):
            raise TypeError(f'{user_class} should be a subclass of {User}.')

        class uc(auth_class, user_class):
            pass

        self.content_class = uc
        self.data = {}

    def select_user(self, userid):
        return self.select_one(userid)
