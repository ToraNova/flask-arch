from . import base
from ...cms.volatile import ContentManager

class UserManager(ContentManager):

    def __init__(self, user_class):
        if not issubclass(user_class, base.User):
            raise TypeError(f'{user_class} should be a subclass of {base.User}.')
        self.content_class = user_class
        self.data = {}

    def select_user(self, userid):
        return self.select_one(userid)
