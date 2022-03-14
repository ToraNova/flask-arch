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

    def prepare(self, rp):
        u, d = self.auth_manager.prepare_login(rp)

        if not isinstance(u, Auth):
            raise exceptions.INVALID_CREDS

        if not u.auth(d):
            raise exceptions.INVALID_CREDS

        return (rp, u)

    def execute(self, rp, u):
        # auth success
        login_user(u)
        self.callback(tags.SUCCESS, u.get_id())
        return self.reroute()

class RegisterBlock(PrepExecBlock):

    def prepare(self, rp):
        u = self.auth_manager.Content(rp, None)
        u.before_insert(rp, u)
        return (rp, u)

    def execute(self, rp, u):
        # insert new user
        identifier = self.auth_manager.insert(u)
        self.auth_manager.commit() # commit insertion
        u.after_insert(rp, u)
        self.callback(tags.SUCCESS, u.get_id())
        return self.reroute()

class RenewBlock(PrepExecBlock):

    @property
    def default_access_policy(self):
        return login_required

    def prepare(self, rp):
        # shallow copy a user (as opposed to deepcopy)
        u = copy.deepcopy(current_user)
        # update current user from request
        u.modify(rp, u)
        u.before_update(rp, u)
        logout_user() # logout user from flask-login
        return (rp, u)

    def execute(self, rp, u):
        # insert the updated new user
        login_user(u) # login the copy
        self.auth_manager.update(u)
        self.auth_manager.commit() # commit insertion
        u.after_update(rp, u)
        self.callback(tags.SUCCESS, u.get_id())
        return self.reroute()

class ResetBlock(PrepExecBlock):

    def prepare(self, rp):
        u = self.auth_manager.prepare_reset(rp)
        if not isinstance(u, Auth):
            raise exceptions.INVALID_CREDS
        u.reset(rp)  # reset auth data
        return (rp, u)

    def execute(self, rp, u):
        self.auth_manager.update(u)
        self.auth_manager.commit() # commit insertion
        u.after_update(rp, u)
        self.callback(tags.SUCCESS, u.get_id())
        return self.reroute()

class RemoveBlock(PrepExecBlock):

    @property
    def default_access_policy(self):
        return login_required

    def prepare(self, rp):
        # shallow copy a user (as opposed to deepcopy)
        u = copy.deepcopy(current_user)
        # update current user from request
        u.deinit(rp, u)
        logout_user()
        return (rp, u)

    def execute(self, rp, u):
        # insert new user
        self.auth_manager.delete(u)
        self.auth_manager.commit() # commit insertion
        u.after_delete(rp, u)
        self.callback(tags.SUCCESS, u.get_id())
        return self.reroute()
