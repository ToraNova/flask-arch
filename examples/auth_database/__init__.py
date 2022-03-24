# a simple flask-arch example
from flask import Flask, request, render_template, redirect, url_for, flash, abort

from flask_arch.cms import SQLDBConnection
from flask_arch.builtins import AuthArch, PasswordAuth
from flask_arch.user import SQLUserManager, SQLRole

from sqlalchemy.ext.declarative import declarative_base

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.config['DBURI'] = 'sqlite:///auth_example.db' # specify database uri
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    # prevent pytest from erroring on metadata redefinition
    # this is also useful when u want to define your own userclass
    my_declarative_base = declarative_base()

    db_conn = SQLDBConnection(app.config['DBURI'], my_declarative_base)
    db_conn.configure_teardown(app)

    # use a volatile dictionary to handle user, users are ephemeral
    user_manager = SQLUserManager(PasswordAuth, db_conn)

    # for first time
    if not user_manager.table_exists:
        # create table
        user_manager.create_table()
        # first time
        u = user_manager.Content.create_default_with_form(username='jason', password='hunter2', password_confirm='hunter2')
        user_manager.insert(u)
        user_manager.commit()


    persist = AuthArch(user_manager, 'database_test')

    persist.init_app(app)

    @app.route('/')
    def root():
        return render_template('root.html')

    return app
