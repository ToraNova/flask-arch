# a simple flask-arch example
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_arch.auth import Arch
from flask_arch.auth.user import SQLPasswordUser
from flask_arch.cms import SQLContentManager
from flask_login import current_user, login_required

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.config['DBURI'] = 'sqlite:///auth_example.db' # specify database uri
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    # use a volatile dictionary to handle user, users are ephemeral
    user_manager = SQLContentManager(SQLPasswordUser, app.config['DBURI'])

    # for first time
    init_add = not user_manager.table_exists()

    # create table
    try:
        user_manager.create_table()
    except Exception as e:
        print(e)
        pass

    if init_add:
        # first time
        user = SQLPasswordUser('jason', 'hunter2')
        user_manager.insert(user)
        user_manager.commit()


    persist = Arch(user_manager, 'database_test')

    persist.init_app(app)

    @app.route('/')
    def root():
        return render_template('root.html')

    return app
