# basic authentication (username, password)
# no database systems, users defined by python scripts

import copy
from flask import request, url_for
from jinja2.exceptions import TemplateNotFound
from flask_arch import BaseArch, exceptions, tags
from flask_arch.cms import BaseContentManager
from flask_login import login_user, logout_user, LoginManager, login_required, current_user


def _default_cb_login_invalid(arch, e):
    arch.flash('invalid credentials', 'err')
    return arch.render(), 401


def _default_cb_user_error(arch, e):
    arch.flash(e.msg, 'err')
    return arch.render(), e.code

def _default_cb_int_error(arch, e):
    arch.flash(str(e), 'err')
    return arch.render(),


# basic.Arch
# templates: login, profile, unauth
# reroutes: login, logout
class Arch(BaseArch):

    def __init__(self, user_manager, arch_name='default-auth-basic', templates={}, reroutes={}, reroutes_kwarg={}, custom_callbacks={}, url_prefix=None, routes_disabled=[],):
        '''
        initialize the architecture for the flask_arch
        templ is a dictionary that returns user specified templates to user on given routes
        reroutes is a dictionary that reroutes the user after certain actions on given routes
        '''
        super().__init__(arch_name, templates, reroutes, reroutes_kwarg, custom_callbacks, url_prefix)

        self._type_test(user_manager, BaseContentManager, 'user_manager')
        self._type_test(routes_disabled, list, 'routes_disabled')
        self.user_manager = user_manager
        self._rdisable = routes_disabled

        self._default_tp('login', 'login.html')
        self._default_tp('profile', 'profile.html')
        self._default_tp('unauth','unauth.html')
        self._default_tp('register', 'register.html')
        self._default_tp('update', 'update.html')
        self._default_tp('delete', 'delete.html')

        self._default_rt('login', f'{arch_name}.profile')
        self._default_rt('logout',f'{arch_name}.login')
        self._default_rt('register', f'{arch_name}.login') # go to login after registration
        self._default_rt('update', f'{arch_name}.profile') # go to profile after profile update
        self._default_rt('delete', f'{arch_name}.login') # go to login after account delete

        # callbacks
        self._default_cb('login', tags.INVALID_USER, _default_cb_login_invalid)
        self._default_cb('login', tags.INVALID_AUTH, _default_cb_login_invalid)

        for route in ['login', 'logout', 'register', 'update', 'delete']:
            self._default_cb(route, tags.SUCCESS,
                lambda arch, e: arch.flash(f'{arch.get_route_key()} successful', 'ok')
            )
            self._default_cb(route, tags.USER_ERROR, _default_cb_user_error)

        self._default_cb('register', tags.INTEGRITY_ERROR, lambda arch, e: arch.flash('user exists', 'warn'))
        self._default_cb('update', tags.INTEGRITY_ERROR, lambda arch, e: arch.flash(str(e), 'warn'))
        self._default_cb('delete', tags.INTEGRITY_ERROR, lambda arch, e: arch.flash(str(e), 'warn'))

    def setup_login_route(self):
        @self.bp.route('/login', methods=['GET','POST'])
        def login():
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
                    self.user_manager.rollback() # rollback
                    self.server_error(e)

            # render template
            return self.render(), 200

    def setup_logout_route(self):
        @self.bp.route('/logout')
        def logout():
            identifier = current_user.id
            logout_user()
            self.custom(tags.SUCCESS, identifier)
            return self.reroute()

    def setup_profile_route(self):
        @self.bp.route('/profile')
        @login_required
        def profile():
            return self.render()

    def setup_register_route(self):
        @self.bp.route('/register', methods=['GET', 'POST'])
        def register():
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

    def setup_update_route(self):
        @self.bp.route('/update', methods=['GET', 'POST'])
        @login_required
        def update():
            if request.method == 'POST':
                user, identifier = None, None
                try:
                    # shallow copy a user (as opposed to deepcopy)
                    user = copy.deepcopy(current_user)
                    identifier = user.id
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

    def setup_delete_route(self):
        @self.bp.route('/delete', methods=['GET', 'POST'])
        @login_required
        def delete():
            if request.method == 'POST':
                user, identifier = None, None
                try:
                    # shallow copy a user (as opposed to deepcopy)
                    user = copy.deepcopy(current_user)
                    identifier = user.id
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

        lman = LoginManager()
        @lman.unauthorized_handler
        def unauthorized():
            self.abort(401)

        @lman.user_loader
        def loader(userid):
            user = self.user_manager.select_user(userid)
            user.is_authenticated = True
            return user

        self.setup_login_route()
        self.setup_logout_route()

        # create route for 'profile' if not disabled
        if 'profile' not in self._rdisable:
            self.setup_profile_route()

        # create route for 'register' if not disabled
        if 'register' not in self._rdisable:
            self.setup_register_route()

        # create route for 'update' if not disabled
        if 'update' not in self._rdisable:
            self.setup_update_route()

        # create route for 'delete' if not disabled
        if 'delete' not in self._rdisable:
            self.setup_delete_route()

        lman.init_app(app)

        app.register_blueprint(self.bp)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.user_manager.shutdown_session()
