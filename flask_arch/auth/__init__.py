# basic authentication (username, password)
# no database systems, users defined by python scripts

import copy
from flask import request, url_for
from jinja2.exceptions import TemplateNotFound
from flask_login import login_user, logout_user, LoginManager, login_required, current_user

from .. import BaseArch, RouteArch, exceptions, tags, callbacks
from ..cms import BaseContentManager


# basic.Arch
# templates: login, profile, unauth
# reroutes: login, logout
class Arch(BaseArch):

    def __init__(self, user_manager, arch_name='auth', templates={}, reroutes={}, reroutes_kwarg={}, custom_callbacks={}, url_prefix=None, routes_disabled=[],):
        '''
        initialize the architecture for the flask_arch
        templ is a dictionary that returns user specified templates to user on given routes
        reroutes is a dictionary that reroutes the user after certain actions on given routes
        '''
        self.type_test(routes_disabled, list, 'routes_disabled')
        self._rdisable = routes_disabled
        self.type_test(user_manager, BaseContentManager, 'user_manager')
        self.user_manager = user_manager

        LOGIN   = 'login'
        LOGOUT  = 'logout'
        PROFILE = 'profile'
        INSERT  = 'register'
        UPDATE  = 'renew'
        DELETE  = 'remove'

        routing_rules = [
            # keyword, view_function, reroute, options
            RouteArch(PROFILE, self.route_profile),
            RouteArch(LOGOUT, self.route_logout, LOGIN),
            RouteArch(LOGIN, self.route_login,  PROFILE, methods=['GET', 'POST']),
            # do not add the rule if route is disabled
            RouteArch(INSERT, self.route_insert, LOGIN, methods=['GET', 'POST'])\
                    if INSERT not in routes_disabled else None,
            RouteArch(UPDATE, self.route_update, PROFILE, methods=['GET', 'POST'])\
                    if UPDATE not in routes_disabled else None,
            RouteArch(DELETE, self.route_delete, LOGIN, methods=['GET', 'POST'])\
                    if DELETE not in routes_disabled else None,
        ]

        super().__init__(arch_name, routing_rules, templates, reroutes, reroutes_kwarg, custom_callbacks, url_prefix)

        self.default_cb(LOGIN, tags.INVALID_USER, callbacks.default_login_invalid)
        self.default_cb(LOGIN, tags.INVALID_AUTH, callbacks.default_login_invalid)

        for ra in self.routing_rules:
            self.default_cb(ra.keyword, tags.SUCCESS, callbacks.default_success)
            self.default_cb(ra.keyword, tags.USER_ERROR, callbacks.default_user_error)
            #self.default_cb(ra.keyword, tags.INTEGRITY_ERROR, callbacks.default_int_error)

        self.default_cb(INSERT, tags.INTEGRITY_ERROR,
                lambda arch, e: arch.flash('already exist', 'warn'))
        self.default_cb(UPDATE, tags.INTEGRITY_ERROR,
                lambda arch, e: arch.flash(str(e), 'warn'))
        self.default_cb(DELETE, tags.INTEGRITY_ERROR,
                lambda arch, e: arch.flash(str(e), 'warn'))

    def route_login(self):
        if request.method == 'POST':
            identifier, auth_data = None, None
            try:
                identifier, auth_data = self.user_manager.content_class.parse_auth_data(
                    request.form.copy(),
                )
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e)
            except Exception as e:
                # client error
                self.client_error(e)

            try:
                user = self.user_manager.select_user(identifier)
                if user is None:
                    return self.custom(tags.INVALID_USER, identifier)

                if not user.auth(auth_data):
                    return self.custom(tags.INVALID_AUTH, identifier)

                # auth success
                login_user(user)
                self.custom(tags.SUCCESS, identifier)
                return self.reroute()
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e)
            except Exception as e:
                # server error: unexpected exception
                self.user_manager.rollback()  # rollback
                self.server_error(e)

        # render template
        return self.render(), 200

    def route_logout(self):
        identifier = current_user.get_id()
        logout_user()
        self.custom(tags.SUCCESS, identifier)
        return self.reroute()

    def route_insert(self):
        if request.method == 'POST':
            user = None
            try:
                # create user from request
                user = self.user_manager.content_class.create(request.form.copy())
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e)
            except Exception as e:
                # client error
                self.client_error(e)

            try:
                # insert new user
                identifier = self.user_manager.insert(user)
                self.user_manager.commit() # commit insertion
                self.custom(tags.SUCCESS, identifier)
                return self.reroute()
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e) # handle user error
            except exceptions.IntegrityError as e:
                self.user_manager.rollback() # rollback
                return self.custom(tags.INTEGRITY_ERROR, e) # handle integrity error
            except Exception as e:
                # server error: unexpected exception
                self.user_manager.rollback() # rollback
                self.server_error(e)

        return self.render()

    @login_required
    def route_profile(self):
        return self.render()

    @login_required
    def route_update(self):
        if request.method == 'POST':
            user, identifier = None, None
            try:
                # shallow copy a user (as opposed to deepcopy)
                user = copy.deepcopy(current_user)
                identifier = user.get_id()
                # update current user from request
                user.update(request.form.copy())
                logout_user() # logout user from flask-login
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e)
            except Exception as e:
                # client error
                self.client_error(e)

            try:
                # insert the updated new user
                login_user(user) # login the copy
                self.user_manager.update(user)
                self.user_manager.commit() # commit insertion
                self.custom(tags.SUCCESS, identifier)
                return self.reroute()
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e) # handle user error
            except exceptions.IntegrityError as e:
                self.user_manager.rollback() # rollback
                return self.custom(tags.INTEGRITY_ERROR, e) # handle integrity error
            except Exception as e:
                # server error: unexpected exception
                self.user_manager.rollback() # rollback
                self.server_error(e)

        return self.render()

    @login_required
    def route_delete(self):
        if request.method == 'POST':
            user, identifier = None, None
            try:
                # shallow copy a user (as opposed to deepcopy)
                user = copy.deepcopy(current_user)
                identifier = user.get_id()
                # update current user from request
                user.delete(request.form.copy())
                logout_user()
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e)
            except Exception as e:
                # client error
                self.client_error(e)

            try:
                # insert new user
                self.user_manager.delete(user)
                self.user_manager.commit() # commit insertion
                self.custom(tags.SUCCESS, identifier)
                return self.reroute()
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e) # handle user error
            except exceptions.IntegrityError as e:
                self.user_manager.rollback() # rollback
                return self.custom(tags.INTEGRITY_ERROR, e) # handle integrity error
            except Exception as e:
                # server error: unexpected exception
                self.user_manager.rollback() # rollback
                self.server_error(e)

        return self.render()

    def init_app(self, app):
        super().init_app(app)

        lman = LoginManager()
        @lman.unauthorized_handler
        def unauthorized():
            self.abort(401)

        @lman.user_loader
        def loader(userid):
            user = self.user_manager.select_user(userid)
            user.is_authenticated = True
            return user

        lman.init_app(app)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.user_manager.shutdown_session()
