# basic authentication (username, password)
# no database systems, users defined by python scripts

import copy
from flask import request, url_for, abort
from jinja2.exceptions import TemplateNotFound
from flask_login import login_user, logout_user, LoginManager, login_required, current_user

from .blocks import LoginBlock, LogoutBlock, IUDBlock, AuthManageBlock
from .. import BaseArch, tags, callbacks
from ..utils import ensure_type
from ..blocks.basic import RenderBlock
from ..cms import BaseContentManager


# basic.Arch
# templates: login, profile, unauth
# reroutes: login, logout
class Arch(BaseArch):

    def __init__(self, user_manager, arch_name='auth', templates={}, reroutes={}, reroutes_kwargs={}, custom_callbacks={}, url_prefix=None, routes_disabled=[],):
        '''
        initialize the architecture for the flask_arch
        templ is a dictionary that returns user specified templates to user on given routes
        reroutes is a dictionary that reroutes the user after certain actions on given routes
        '''
        ensure_type(routes_disabled, list, 'routes_disabled')
        ensure_type(user_manager, BaseContentManager, 'user_manager')
        self.user_manager = user_manager

        LOGIN   = 'login'
        LOGOUT  = 'logout'
        PROFILE = 'profile'
        INSERT  = 'register'
        UPDATE  = 'renew'
        DELETE  = 'remove'

        route_blocks = []

        r = RenderBlock(PROFILE, access_policy=login_required)
        route_blocks.append(r)

        r = LoginBlock(LOGIN, user_manager, reroute_to=PROFILE)
        r.set_custom_callback(tags.INVALID_USER, callbacks.default_login_invalid)
        r.set_custom_callback(tags.INVALID_AUTH, callbacks.default_login_invalid)
        route_blocks.append(r)

        r = LogoutBlock(LOGOUT, user_manager, reroute_to=LOGIN)
        route_blocks.append(r)

        if INSERT not in routes_disabled:
            r = IUDBlock(INSERT, user_manager, 'insert',
                    reroute_to=LOGIN)
            r.set_custom_callback(tags.INTEGRITY_ERROR,
                    lambda arch, e: arch.flash('already exist', 'warn'))
            route_blocks.append(r)

        if UPDATE not in routes_disabled:
            r = IUDBlock(UPDATE, user_manager, 'update',
                    reroute_to=PROFILE, access_policy=login_required)
            r.set_custom_callback(tags.INTEGRITY_ERROR,
                    lambda arch, e: arch.flash(str(e), 'warn'))
            route_blocks.append(r)

        if DELETE not in routes_disabled:
            r = IUDBlock(DELETE, user_manager, 'delete',
                    reroute_to=LOGIN, access_policy=login_required)
            r.set_custom_callback(tags.INTEGRITY_ERROR,
                    lambda arch, e: arch.flash(str(e), 'warn'))
            route_blocks.append(r)

        for r in route_blocks:
            r.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            r.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)

        super().__init__(arch_name, route_blocks, templates, reroutes, reroutes_kwargs, custom_callbacks, url_prefix)

    def init_app(self, app):
        super().init_app(app)

        lman = LoginManager()
        @lman.unauthorized_handler
        def unauthorized():
            abort(401)

        @lman.user_loader
        def loader(userid):
            user = self.user_manager.select_user(userid)
            user.is_authenticated = True
            return user

        lman.init_app(app)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.user_manager.shutdown_session()
