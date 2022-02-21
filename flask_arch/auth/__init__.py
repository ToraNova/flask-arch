# basic authentication (username, password)
# no database systems, users defined by python scripts

from flask import request, url_for
from flask_login import LoginManager, login_required
from jinja2.exceptions import TemplateNotFound
from flask_arch import BaseArch

# basic.Arch
# templates: login, profile, unauth
# reroutes: login, logout
class Arch(BaseArch):
    def __init__(self, auth_handler, arch_name='default-auth-basic', templates = {}, reroutes = {}, reroutes_kwarg = {}, custom_callbacks = {}, url_prefix = None):
        '''
        initialize the architecture for the flask_arch
        templ is a dictionary that returns user specified templates to user on given routes
        reroutes is a dictionary that reroutes the user after certain actions on given routes
        '''
        super().__init__(arch_name, templates, reroutes, reroutes_kwarg, custom_callbacks, url_prefix)
        self.auth_handler = auth_handler
        self._default_tp('login', 'login.html')
        self._default_tp('profile', 'profile.html')
        self._default_tp('unauth','unauth.html')
        self._default_rt('login', f'{arch_name}.profile')
        self._default_rt('logout',f'{arch_name}.login')

    def render_unauth(self):
        try:
            return self._render('unauth'), 401
        except TemplateNotFound:
            return 'login required. please login at %s' % url_for(f'{self._arch_name}.login', _external=True), 401

    def init_app(self, app):

        lman = LoginManager()

        @lman.unauthorized_handler
        def unauth():
            return self.render_unauth()

        @lman.user_loader
        def loader(uid):
            u = self.auth_handler.find_user_by_id(uid)
            u.is_authenticated = True
            return u

        @self.bp.route('/login', methods=['GET','POST'])
        def login():
            return self.auth_handler.login(self, request)

        @self.bp.route('/profile')
        @login_required
        def profile():
            return self.render()

        @self.bp.route('/logout')
        def logout():
            return self.auth_handler.logout(self, request)

        app.register_blueprint(self.bp)
        lman.init_app(app)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            pass
