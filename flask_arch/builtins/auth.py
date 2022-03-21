# basic authentication (username, password)
# no database systems, users defined by python scripts

from flask import abort
from flask_login import LoginManager, login_required

from .. import base, tags, callbacks
from ..auth import AuthViewBlock, AuthFileBlock, AuthLoginBlock, AuthLogoutBlock, AuthRegisterBlock, AuthRenewBlock, AuthResetBlock, AuthRemoveBlock
from ..auth.base import AuthManager
from ..utils import ensure_type

# basic.Arch
class Arch(base.Arch):

    def __init__(self, user_manager, arch_name='auth', **kwargs):
        '''
        initialize the architecture for the flask_arch
        templ is a dictionary that returns user specified templates to user on given routes
        reroutes is a dictionary that reroutes the user after certain actions on given routes
        '''
        super().__init__(arch_name, **kwargs)
        ensure_type(user_manager, AuthManager, 'user_manager')

        LOGIN   = 'login'
        LOGOUT  = 'logout'
        PROFILE = 'profile'
        INSERT  = 'register'
        UPDATE  = 'renew'
        RESET  = 'reset'
        DELETE  = 'remove'
        FILE = 'file'

        rb = AuthViewBlock(PROFILE, user_manager)
        self.add_route_block(rb)

        rb = AuthFileBlock(FILE, user_manager)
        self.add_route_block(rb)

        rb = AuthLoginBlock(LOGIN, user_manager, reroute_to=PROFILE)
        self.add_route_block(rb)

        rb = AuthLogoutBlock(LOGOUT, user_manager, reroute_to=LOGIN)
        self.add_route_block(rb)

        rb = AuthRegisterBlock(INSERT, user_manager, reroute_to=LOGIN)
        self.add_route_block(rb)

        rb = AuthRenewBlock(UPDATE, user_manager, reroute_to=PROFILE)
        self.add_route_block(rb)

        rb = AuthResetBlock(RESET, user_manager, reroute_to=LOGIN)
        self.add_route_block(rb)

        rb = AuthRemoveBlock(DELETE, user_manager, reroute_to=LOGIN)
        self.add_route_block(rb)

        for rb in self.route_blocks.values():
            rb.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            rb.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)

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

    def init_app(self, app):
        super().init_app(app)

        self.login_manager.init_app(app)
