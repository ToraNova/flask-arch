# a simple flask-arch example
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_login import current_user, login_required

from flask_arch.builtins import AuthArch, PasswordAuth
from flask_arch.user import ProcMemUserManager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    # use a volatile manager to handle user, users are ephemeral
    user_manager = ProcMemUserManager(PasswordAuth)

    # this user will persist because it is defined in the script
    u = user_manager.Content.create_default_with_form(username='jason', password='hunter2', password_confirm='hunter2')
    user_manager.insert(u)

    # create arch and initialize the app with it
    minimal = AuthArch(user_manager, 'simple',
        # disable register, delete and update route
        routes_disabled = ['register', 'renew', 'remove'],
    )

    # both arch may share the same user manager
    featured = AuthArch(user_manager, 'iud',
        custom_templates = {
            'login': 'signin.html',
            'profile': 'home.html',
            'renew': 'password.html',
        },
        # define custom callbacks
        custom_callbacks = {
            'login':{
                # for BasicPasswordUser, get_id() is equivalent to human-friendly identifier a.k.a username
                'success': lambda arch, e: arch.flash(f'welcome back {current_user.get_id()}')
            },
        },
    )

    minimal.init_app(app)
    featured.init_app(app)

    @app.route('/')
    def root():
        return render_template('root.html')

    @app.route('/treasure')
    @login_required
    def treasure():
        return 'secret'

    return app
