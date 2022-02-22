# a simple flask-arch example
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_arch.auth import Arch
from flask_arch.auth.user import PasswordUser
from flask_arch.cms import VolatileDictionary
from flask_login import current_user, login_required

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    # use a volatile dictionary to handle user, users are ephemeral
    user_manager = VolatileDictionary(PasswordUser)

    # this user will persist because it is defined in the script
    user = PasswordUser('jason', 'hunter2')
    user_manager.insert(user)

    # create arch and initialize the app with it
    minimal = Arch(user_manager, 'simple',
        # disable register, delete and update route
        routes_disabled = ['delete', 'register', 'update'],
    )

    # both arch may share the same user manager
    featured = Arch(user_manager, 'iud',
        templates = {
            'login': 'signin.html',
            'profile': 'home.html',
            'update': 'password.html',
        },
        # define custom callbacks
        custom_callbacks = {
            'login':{
                'success': lambda arch, e: arch.flash(f'welcome back {current_user.name}')
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
