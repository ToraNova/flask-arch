from datetime import datetime, timezone, timedelta
from flask import Flask, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect

from flask_arch import tags
from flask_arch.builtins import AuthArch, UserManageArch, CMSArch, PasswordAuth
from flask_arch.user import SQLUserManager, access_policies
from flask_arch.cms import SQLContentManager, SQLDBConnection
from flask_arch.exceptions import UserError

from . import transactionals, accounts
from .models import MyRole, MyUser, Project, my_declarative_base
from .auth import MyAuth

from sqlalchemy.ext.declarative import declarative_base

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    app.config['DBURI'] = 'sqlite:///starter_1.db' # specify database uri
    app.testing = False

    if test_config:
        app.config.from_mapping(test_config)

    db_conn = SQLDBConnection(app.config['DBURI'], my_declarative_base)
    db_conn.configure_teardown(app)

    # primary user manager
    userm = SQLUserManager(MyAuth, db_conn, user_class=MyUser)

    # for login/auth
    aa = AuthArch(userm, custom_templates_dir='auth',
            routes_disabled=['remove'] # users can't delete their own account
    )
    aa.init_app(app)

    # for managing users
    uma = UserManageArch(userm, custom_templates_dir='users', routes_disabled=['add'])
    uma.init_app(app)

    if not userm.table_exists:
        userm.create_table()
        u = userm.Content.create_default_with_form(
                email='admin@test.d',
                username='jason',
                role_id=1,
                password='hunter2',
                password_confirm='hunter2'
            )
        userm.insert(u)

        u = userm.Content.create_default_with_form(
                email='user@test.d',
                username='uat',
                role_id=2,
                password='asdasd',
                password_confirm='asdasd'
            )
        userm.insert(u)

        userm.commit()


    projm = SQLContentManager(Project, db_conn)
    if not projm.table_exists:
        projm.create_table()

    ca_proj = CMSArch(projm, 'project', custom_templates_dir='projects',
            custom_reroutes={
                'update': 'project.view'
            }
        )
    ca_proj.init_app(app)


    rolem = SQLContentManager(MyRole, db_conn)
    ca_role = CMSArch(rolem, 'role', custom_templates_dir='roles')
    ca_role.init_app(app)

    if not rolem.table_exists:
        rolem.create_table()

        r = rolem.Content.create_default_with_form(name='admin')
        # has all the privileges
        r.set_list_privileges([
            uma.privileges.VIEW, uma.privileges.ADD, uma.privileges.MOD, uma.privileges.DEL,
            ca_role.privileges.VIEW, ca_role.privileges.INSERT,
            ca_role.privileges.UPDATE, ca_role.privileges.DELETE,
            ca_proj.privileges.VIEW, ca_proj.privileges.INSERT,
            ca_proj.privileges.UPDATE, ca_proj.privileges.DELETE,
        ])
        rolem.insert(r)

        r = rolem.Content.create_default_with_form(name='normal')
        r.set_list_privileges([
            uma.privileges.VIEW,  # can see other users
            ca_proj.privileges.VIEW, ca_proj.privileges.INSERT, # has view/insert/update/delete privileges
            ca_proj.privileges.UPDATE, ca_proj.privileges.DELETE, # on the 'project' content
        ])
        rolem.insert(r)

        rolem.commit()

    csrf = CSRFProtect()
    csrf.init_app(app)

    @app.template_filter()
    def from_timestamp(val, fmt='%Y/%m/%d %H:%M'):
        dt = datetime.fromtimestamp(val, tz=timezone.utc)
        dt += timedelta(hours=8) # gmt+8
        return dt.strftime(fmt)

    @app.template_filter()
    def from_datetime(val, fmt='%Y/%m/%d %H:%M:%S'):
        if isinstance(val, datetime):
            return val.strftime(fmt)
        else:
            return 'no record'

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))
        #return render_template('root.html')

    @app.route('/dashboard')
    @access_policies.login_required
    def dashboard():
        return render_template('dashboard.html')

    transactionals.init_app(app, userm)
    accounts.init_app(app, userm)

    return app
