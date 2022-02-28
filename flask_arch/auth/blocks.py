import copy
from flask import request
from flask_login import login_user, logout_user, current_user

from .. import tags, exceptions
from ..cms import ContentManageBlock

class AuthManageBlock(ContentManageBlock):

    def __init__(self, keyword, user_manager, **kwargs):
        super().__init__(keyword, user_manager, **kwargs)
        self.user_manager = self.content_manager

class LogoutBlock(AuthManageBlock):

    def view(self):
        if not current_user.is_authenticated:
            return self.reroute()
        identifier = current_user.get_id()
        logout_user()
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()

class LoginBlock(AuthManageBlock):

    @property
    def default_methods(self):
        return ['GET', 'POST']

    def view(self):
        if request.method == 'POST':
            identifier, auth_data = None, None
            try:
                identifier, auth_data = self.user_manager.content_class.parse_auth_data(
                    request.form.copy(),
                )
            except exceptions.UserError as e:
                return self.callback(tags.USER_ERROR, e)
            except Exception as e:
                # client error
                self.client_error(e)

            try:
                user = self.user_manager.select_user(identifier)
                if user is None:
                    return self.callback(tags.INVALID_USER, identifier)

                if not user.auth(auth_data):
                    return self.callback(tags.INVALID_AUTH, identifier)

                # auth success
                login_user(user)
                self.callback(tags.SUCCESS, identifier)
                return self.reroute()
            except exceptions.UserError as e:
                return self.callback(tags.USER_ERROR, e)
            except Exception as e:
                # server error: unexpected exception
                self.user_manager.rollback()  # rollback
                self.server_error(e)

        # render template
        return self.render(), 200

class IUDBlock(AuthManageBlock):

    @property
    def default_methods(self):
        return ['GET', 'POST']

    def __init__(self, keyword, user_manager, action, **kwargs):
        super().__init__(keyword, user_manager, **kwargs)
        self.action = action

        if action == 'insert':
            def prepare():
                user = self.user_manager.create(request.form.copy())
                return (user,)

            def execute(user):
                # insert new user
                identifier = self.user_manager.insert(user)
                self.user_manager.commit() # commit insertion
                self.callback(tags.SUCCESS, identifier)
                return self.reroute()

        elif action == 'update':

            def prepare():
                # shallow copy a user (as opposed to deepcopy)
                user = copy.deepcopy(current_user)
                identifier = user.get_id()
                # update current user from request
                user.update(request.form.copy())
                logout_user() # logout user from flask-login
                return (identifier, user)

            def execute(identifier, user):
                # insert the updated new user
                login_user(user) # login the copy
                self.user_manager.update(user)
                self.user_manager.commit() # commit insertion
                self.callback(tags.SUCCESS, identifier)
                return self.reroute()

        elif action == 'delete':

            def prepare():
                # shallow copy a user (as opposed to deepcopy)
                user = copy.deepcopy(current_user)
                identifier = user.get_id()
                # update current user from request
                user.delete(request.form.copy())
                logout_user()
                return (identifier, user)

            def execute(identifier, user):
                # insert new user
                self.user_manager.delete(user)
                self.user_manager.commit() # commit insertion
                self.callback(tags.SUCCESS, identifier)
                return self.reroute()

        else:
            raise ValueError(f'invalid action \'{action}\'')

        self.prepare = prepare
        self.execute = execute

    def view(self):
        if request.method == 'POST':
            try:
                aargs = self.prepare()
            except exceptions.UserError as e:
                return self.callback(tags.USER_ERROR, e)
            except Exception as e:
                # client error
                self.client_error(e)

            try:
                return self.execute(*aargs)
            except exceptions.UserError as e:
                return self.callback(tags.USER_ERROR, e) # handle user error
            except exceptions.IntegrityError as e:
                self.user_manager.rollback() # rollback
                return self.callback(tags.INTEGRITY_ERROR, e) # handle integrity error
            except Exception as e:
                # server error: unexpected exception
                self.user_manager.rollback() # rollback
                self.server_error(e)

        return self.render()
