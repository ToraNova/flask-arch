# basic authentication (username, password)
# no database systems, users defined by python scripts

from flask import abort
from flask_login import LoginManager, login_required

from .blocks import LoginBlock, LogoutBlock, IUDBlock
from .. import BaseArch, tags, callbacks
from ..utils import ensure_type
from ..blocks.basic import RenderBlock
from ..cms import BaseContentManager


# basic.Arch
class Arch(BaseArch):

    def __init__(self, user_manager, arch_name='auth', routes_disabled=[], route_blocks=[], **kwargs):
        '''
        initialize the architecture for the flask_arch
        templ is a dictionary that returns user specified templates to user on given routes
        reroutes is a dictionary that reroutes the user after certain actions on given routes
        '''
        ensure_type(user_manager, BaseContentManager, 'user_manager')
        ensure_type(routes_disabled, list, 'routes_disabled')
        ensure_type(route_blocks, list, 'custom_route_blocks')

        LOGIN   = 'login'
        LOGOUT  = 'logout'
        PROFILE = 'profile'
        INSERT  = 'register'
        UPDATE  = 'renew'
        DELETE  = 'remove'

        rbs = route_blocks.copy()

        if PROFILE not in rbs:
            r = RenderBlock(PROFILE, access_policy=login_required)
            rbs.append(r)

        if LOGIN not in rbs:
            r = LoginBlock(LOGIN, user_manager, reroute_to=PROFILE)
            r.set_custom_callback(tags.INVALID_USER, callbacks.default_login_invalid)
            r.set_custom_callback(tags.INVALID_AUTH, callbacks.default_login_invalid)
            rbs.append(r)

        if LOGOUT not in rbs:
            r = LogoutBlock(LOGOUT, user_manager, reroute_to=LOGIN)
            rbs.append(r)

        if INSERT not in rbs and INSERT not in routes_disabled:
            r = IUDBlock(INSERT, user_manager, 'insert',
                    reroute_to=LOGIN)
            r.set_custom_callback(tags.INTEGRITY_ERROR,
                    lambda arch, e: arch.flash('already exist', 'warn'))
            rbs.append(r)

        if UPDATE not in rbs and UPDATE not in routes_disabled:
            r = IUDBlock(UPDATE, user_manager, 'update',
                    reroute_to=PROFILE, access_policy=login_required)
            r.set_custom_callback(tags.INTEGRITY_ERROR,
                    lambda arch, e: arch.flash(str(e), 'warn'))
            rbs.append(r)

        if DELETE not in rbs and DELETE not in routes_disabled:
            r = IUDBlock(DELETE, user_manager, 'delete',
                    reroute_to=LOGIN, access_policy=login_required)
            r.set_custom_callback(tags.INTEGRITY_ERROR,
                    lambda arch, e: arch.flash(str(e), 'warn'))
            rbs.append(r)

        for r in rbs:
            r.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            r.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)

        self.login_manager = LoginManager()

        @self.login_manager.unauthorized_handler
        def unauthorized():
            abort(401)

        @self.login_manager.user_loader
        def loader(userid):
            user = user_manager.select_user(userid)
            user.is_authenticated = True
            return user

        def shutdown(exception):
            user_manager.shutdown_session(exception)

        self.shutdown = shutdown

        super().__init__(arch_name, rbs, **kwargs)

    def init_app(self, app):
        super().init_app(app)

        self.login_manager.init_app(app)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.shutdown(exception)
