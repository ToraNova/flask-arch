import json

from ..cms.base import Content

class Role(Content):
    __DELIM = ';'

    def __init__(self, name, privileges=[]):
        self.name = name
        self.privileges = '{}'
        for p in privileges:
            self.set_privilege(p, True)

    def set_privilege(self, privilege, set_1=True):
        pd = self.get_privileges()
        if set_1:
            pd[privilege] = 1
        else:
            pd.pop(privilege)
        self.privileges = json.dumps(pd)

    def has_privilege(self, privilege):
        return privilege in self.get_privileges()

    def get_privileges(self):
        return json.loads(self.privileges)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Role):
            return all([self.get_privileges() == other.get_privileges(), self.name == other.name])
        elif isinstance(other, str):
            return self.name == other
        else:
            return False

no_role = Role('no role', [])

class User(Content):
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

    def get_role(self):
        if hasattr(self, 'role') and self.role is not None:
            return self.role
        else:
            return no_role

    # these are different from create, update and delete, in that they are done by the users themselves
    # they are 'self' methods, as opposed to someone else creating/updating and deleting
    @classmethod
    def register(cls, data):
        raise NotImplementedError(f'register method on {cls.__name__} not implemented')

    def renew(self, data):
        raise NotImplementedError(f'renew method on {self.__class__.__name__} not implemented')

    def remove(self, data):
        raise NotImplementedError(f'remove method on {self.__class__.__name__} not implemented')
