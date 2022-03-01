from .base import User

from ...base import BaseUserManager
from ....auth.user import BaseAuth
from ....cms.persist.sql import ContentManager, SQLDeclarativeBase

class UserManager(BaseUserManager, ContentManager):

    def __init__(self, auth_class, database_uri, user_class=User, orm_base=SQLDeclarativeBase):
        if not issubclass(auth_class, BaseAuth):
            raise TypeError(f'{auth_class} should be a subclass of {BaseAuth}.')
        if not issubclass(user_class, User):
            raise TypeError(f'{user_class} should be a subclass of {User}.')

        class AuthUser(auth_class, user_class, orm_base):
            pass

        super().__init__(AuthUser, database_uri, orm_base)

    def select_user(self, userid):
        return self.content_class.query.filter(
            getattr(self.content_class, self.content_class.userid) == userid
        ).first()
