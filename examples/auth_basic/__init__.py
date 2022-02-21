# a simple flask-arch example
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_arch.auth import Arch, handler, user

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    handle1 = handler.Basic()
    user1 = user.Basic('jason', 'hunter2')

    handle1.update_user(user1)

    arch = Arch(handle1, 'auth_basic',
        templates = {
            'profile': 'home.html'
        }
    )

    arch.init_app(app)

    @app.route('/')
    def root():
        return render_template('root.html')

    return app
