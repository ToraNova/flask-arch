import copy
from flask import request
from flask_login import login_user, logout_user, current_user

from .access_policies import login_required, privilege_required

from . import privileges
from .. import tags, exceptions
from .user import BaseAuth
from ..cms import ContentManageBlock, ContentPrepExecBlock
from ..user import BaseUserManager
from ..utils import ensure_type, ensure_callable

class LogoutBlock(ContentManageBlock):

    def __init__(self, keyword, user_manager, **kwargs):
        super().__init__(keyword, user_manager, **kwargs)
        ensure_type(user_manager, BaseUserManager, 'user_manager')
        self.user_manager = self.content_manager

    def view(self):
        if not current_user.is_authenticated:
            # user is not authenticated
            return self.reroute()
        identifier = current_user.get_id()
        logout_user()
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class PrepExecBlock(ContentPrepExecBlock):

    def __init__(self, keyword, user_manager, **kwargs):
        super().__init__(keyword, user_manager, **kwargs)
        ensure_type(user_manager, BaseUserManager, 'user_manager')
        self.user_manager = self.content_manager

class LoginBlock(PrepExecBlock):

    def prepare(self):
        identifier, auth_data = self.user_manager.parse_login(request.form.copy())
        user = self.user_manager.select_user(identifier)
        if not isinstance(user, BaseAuth):
            raise exceptions.INVALID_CREDS

        if not user.auth(auth_data):
            raise exceptions.INVALID_CREDS

        return (identifier, user)

    def execute(self, identifier, user):
        # auth success
        login_user(user)
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class RegisterBlock(PrepExecBlock):

    def prepare(self):
        user = self.user_manager.register(request.form.copy())
        return (user,)

    def execute(self, user):
        # insert new user
        identifier = self.user_manager.insert(user)
        self.user_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class RenewBlock(PrepExecBlock):

    @property
    def default_access_policy(self):
        return login_required

    def prepare(self):
        # shallow copy a user (as opposed to deepcopy)
        user = copy.deepcopy(current_user)
        identifier = user.get_id()
        # update current user from request
        user.renew(request.form.copy())
        logout_user() # logout user from flask-login
        return (identifier, user)

    def execute(self, identifier, user):
        # insert the updated new user
        login_user(user) # login the copy
        self.user_manager.update(user)
        self.user_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class ResetBlock(PrepExecBlock):

    def prepare(self):
        identifier = self.user_manager.parse_reset(request.form.copy())
        user = self.user_manager.select_user(identifier)
        if not isinstance(user, BaseAuth):
            raise exceptions.INVALID_CREDS
        user.reset(request.form.copy())  # reset auth data
        return (identifier, user)

    def execute(self, identifier, user):
        self.user_manager.update(user)
        self.user_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class RemoveBlock(PrepExecBlock):

    @property
    def default_access_policy(self):
        return login_required

    def prepare(self):
        # shallow copy a user (as opposed to deepcopy)
        user = copy.deepcopy(current_user)
        identifier = user.get_id()
        # update current user from request
        user.remove(request.form.copy())
        logout_user()
        return (identifier, user)

    def execute(self, identifier, user):
        # insert new user
        self.user_manager.delete(user)
        self.user_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class UserlstBlock(ContentManageBlock):

    @property
    def default_access_policy(self):
        return privilege_required(privileges.USERSEL)

    def __init__(self, keyword, user_manager, **kwargs):
        super().__init__(keyword, user_manager, **kwargs)
        ensure_type(user_manager, BaseUserManager, 'user_manager')
        self.user_manager = self.content_manager

    def view(self):
        users = self.user_manager.select_all()
        return self.render(data=users)

class UseraddBlock(PrepExecBlock):

    @property
    def default_access_policy(self):
        return privilege_required(privileges.USERADD)

    def prepare(self):
        user = self.user_manager.create(request.form.copy(), current_user)
        return (user,)

    def execute(self, user):
        # insert new user
        identifier = self.user_manager.insert(user)
        self.user_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class UsermodBlock(PrepExecBlock):

    @property
    def default_access_policy(self):
        return privilege_required(privileges.USERMOD)

    def initial(self):
        user = self.user_manager.query(request.args.copy())
        return self.render(target=user)

    def prepare(self):
        user = self.user_manager.modify(request.args.copy(), request.form.copy(), current_user)
        return (user,)

    def execute(self, user):
        # insert new user
        identifier = self.user_manager.update(user)
        self.user_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class UserdelBlock(PrepExecBlock):

    @property
    def default_access_policy(self):
        return privilege_required(privileges.USERDEL)

    def initial(self):
        user = self.user_manager.query(request.args.copy())
        return self.render(target=user)

    def prepare(self):
        user = self.user_manager.query(request.args.copy())
        return (user,)

    def execute(self, user):
        # insert new user
        identifier = self.user_manager.delete(user)
        self.user_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()
