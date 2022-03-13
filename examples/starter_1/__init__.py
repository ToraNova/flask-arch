from flask import Flask, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect

from flask_arch.builtins import AuthArch, UserManageArch, CMSArch, PasswordAuth, privileges
from flask_arch.user import SQLUserManager, access_policies
from flask_arch.cms import SQLContentManager, SQLDBConnection
from flask_arch.exceptions import UserError

from . import transactionals
from .models import User, Role, Project, my_declarative_base
from .auth import MyAuth

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.config['DBURI'] = 'sqlite:///starter_1.db' # specify database uri
    app.testing = False

    if test_config:
        app.config.from_mapping(test_config)

    db_conn = SQLDBConnection(app.config['DBURI'], my_declarative_base)
    db_conn.configure_teardown(app)

    userm = SQLUserManager(MyAuth, db_conn, user_class=User)
    if not userm.table_exists():
        userm.create_table()
        u = userm.construct('admin@test.d', 'jason', 1, 'hunter2')
        userm.insert(u)

        u = userm.construct('user@test.d', 'tifa', 2, 'asdasd')
        userm.insert(u)

        userm.commit()

    rolem = SQLContentManager(Role, db_conn)
    if not rolem.table_exists():
        rolem.create_table()

        r = rolem.construct('admin', [
            privileges.USERSEL, privileges.USERADD, privileges.USERMOD, privileges.USERDEL,
            'role.select', 'role.insert', 'role.update', 'role.delete',
            'project.select', 'project.insert', 'project.update', 'project.delete',
        ])
        rolem.insert(r)

        r = rolem.construct('normal', ['user.select', 'role.select'])
        rolem.insert(r)

        rolem.commit()

    projm = SQLContentManager(Project, db_conn)
    if not projm.table_exists():
        projm.create_table()


    # for login/auth
    a = AuthArch(userm, custom_templates_dir='auth', custom_reroutes={'login': 'dashboard'})
    a.init_app(app)

    # for managing users
    a = UserManageArch(userm, custom_templates_dir='auth', routes_disabled=['useradd', 'userdel'])
    a.init_app(app)

    a = CMSArch(rolem, 'role', custom_templates_dir='roles')
    a.init_app(app)

    a = CMSArch(projm, 'project', custom_templates_dir='projects')
    a.init_app(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))
        #return render_template('root.html')

    @app.route('/dashboard')
    @access_policies.login_required
    def dashboard():
        return render_template('dashboard.html')

    transactionals.bootstrap(app, userm)

    return app
