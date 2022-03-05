import copy
from flask import request
from flask_login import login_user, logout_user, current_user, login_required

from .. import tags, exceptions
from .base import Auth, AuthManager
from ..cms import ContentManageBlock, ContentPrepExecBlock, ContentLstBlock, ContentAddBlock, ContentModBlock, ContentDelBlock
from ..utils import ensure_type

class LogoutBlock(ContentManageBlock):

    def __init__(self, keyword, auth_manager, **kwargs):
        super().__init__(keyword, auth_manager, **kwargs)
        ensure_type(auth_manager, AuthManager, 'auth_manager')
        self.auth_manager = self.content_manager

    def view(self):
        if not current_user.is_authenticated:
            # user is not authenticated
            return self.reroute()
        identifier = current_user.get_id()
        logout_user()
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class PrepExecBlock(ContentPrepExecBlock):

    def __init__(self, keyword, auth_manager, **kwargs):
        super().__init__(keyword, auth_manager, **kwargs)
        ensure_type(auth_manager, AuthManager, 'auth_manager')
        self.auth_manager = self.content_manager

class LoginBlock(PrepExecBlock):

    def prepare(self):
        identifier, auth_data = self.auth_manager.parse_login(request.form.copy())
        user = self.auth_manager.select_user(identifier)
        if not isinstance(user, Auth):
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
        user = self.auth_manager.register(request.form.copy())
        return (user,)

    def execute(self, user):
        # insert new user
        identifier = self.auth_manager.insert(user)
        self.auth_manager.commit() # commit insertion
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
        self.auth_manager.update(user)
        self.auth_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class ResetBlock(PrepExecBlock):

    def prepare(self):
        identifier = self.auth_manager.parse_reset(request.form.copy())
        user = self.auth_manager.select_user(identifier)
        if not isinstance(user, Auth):
            raise exceptions.INVALID_CREDS
        user.reset(request.form.copy())  # reset auth data
        return (identifier, user)

    def execute(self, identifier, user):
        self.auth_manager.update(user)
        self.auth_manager.commit() # commit insertion
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
        self.auth_manager.delete(user)
        self.auth_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()
