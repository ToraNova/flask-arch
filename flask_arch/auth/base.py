# basic authentication (username, password)
# no database systems, users defined by python scripts

from flask import abort
from flask_login import LoginManager, login_required

from .blocks import LoginBlock, LogoutBlock, RegisterBlock, RenewBlock, ResetBlock, RemoveBlock
from .. import BaseArch, tags, callbacks
from ..utils import ensure_type
from ..blocks import RenderBlock
from ..user import BaseUserManager

# basic.Arch
class Arch(BaseArch):

    def __init__(self, user_manager, arch_name='auth', **kwargs):
        '''
        initialize the architecture for the flask_arch
        templ is a dictionary that returns user specified templates to user on given routes
        reroutes is a dictionary that reroutes the user after certain actions on given routes
        '''
        super().__init__(arch_name, **kwargs)
        ensure_type(user_manager, BaseUserManager, 'user_manager')

        LOGIN   = 'login'
        LOGOUT  = 'logout'
        PROFILE = 'profile'
        INSERT  = 'register'
        UPDATE  = 'renew'
        RESET  = 'reset'
        DELETE  = 'remove'

        rb = RenderBlock(PROFILE, access_policy=login_required)
        self.add_route_block(rb)

        rb = LoginBlock(LOGIN, user_manager, reroute_to=PROFILE)
        self.add_route_block(rb)

        rb = LogoutBlock(LOGOUT, user_manager, reroute_to=LOGIN)
        self.add_route_block(rb)

        rb = RegisterBlock(INSERT, user_manager, reroute_to=LOGIN)
        self.add_route_block(rb)

        rb = RenewBlock(UPDATE, user_manager, reroute_to=PROFILE)
        self.add_route_block(rb)

        rb = ResetBlock(RESET, user_manager, reroute_to=LOGIN)
        self.add_route_block(rb)

        rb = RemoveBlock(DELETE, user_manager, reroute_to=LOGIN)
        self.add_route_block(rb)

        for rb in self.route_blocks.values():
            rb.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            rb.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)
            rb.set_custom_callback(tags.INTEGRITY_ERROR, callbacks.default_int_error)

        self.login_manager = LoginManager()

        @self.login_manager.unauthorized_handler
        def unauthorized():
            abort(401)

        @self.login_manager.user_loader
        def loader(userid):
            user = user_manager.select_user(userid)
            if user is None:
                return None
            user.is_authenticated = True
            return user

        def shutdown(exception):
            user_manager.shutdown_session(exception)

        self.shutdown = shutdown


    def init_app(self, app):
        super().init_app(app)

        self.login_manager.init_app(app)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.shutdown(exception)
