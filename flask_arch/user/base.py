import json

from ..cms.base import Content

class Role(Content):

    def __init__(self, rp, actor=None):
        self.name = rp.form['name']
        self.privileges = '{}'

    def set_list_privileges(self, liststr):
        self.privileges = '{}'
        for priv in liststr:
            self.set_privilege(priv, True)

    def set_privilege(self, privilege, set_1=True):
        pd = self.get_privileges()
        if set_1:
            pd[privilege] = 1
        else:
            if privilege in pd:
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

no_role = Role._create_with_form(None, name='no role')

class User(Content):
    '''
    ancestor of all authenticated users
    default attributes: is_authenticated, is_active, is_anonymous, userid (key), id, authd
    '''
    is_anonymous = False
    is_authenticated = False

    # by default, name is used to identify a user easily (i.e., username)
    userid = 'id'

    def __init__(self, rp, actor):
        self.is_active = True

    def modify(self, rp, actor):
        pass

    def get_role(self):
        if hasattr(self, 'role') and self.role is not None:
            return self.role
        else:
            return no_role

    def get_id(self):
        if self.is_anonymous:
            return None
        else:
            return getattr(self, self.userid)
