from .base import User
from .role import User as UserWithRole
from .role import Role

from ....auth.base import Auth, AuthManager
from ....cms.persist.sql import ContentManager

class UserManager(AuthManager, ContentManager):

    def __init__(self, auth_class, db_conn, user_class=User):
        if not issubclass(auth_class, Auth):
            raise TypeError(f'{auth_class} should be a subclass of {Auth}.')
        if not issubclass(user_class, User):
            raise TypeError(f'{user_class} should be a subclass of {User}.')

        class AuthUser(auth_class, user_class, db_conn.orm_base):
            pass

        super().__init__(AuthUser, db_conn)

    def select_user(self, userid):
        return self.Content.query.filter(
            getattr(self.Content, self.Content.userid) == userid
        ).first()
