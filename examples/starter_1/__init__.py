from flask import Flask, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect

from flask_arch import tags
from flask_arch.builtins import AuthArch, UserManageArch, CMSArch, PasswordAuth
from flask_arch.user import SQLUserManager, access_policies
from flask_arch.cms import SQLContentManager, SQLDBConnection
from flask_arch.exceptions import UserError

from . import transactionals
from .models import MyRole, MyUser, Project, my_declarative_base
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

    # primary user manager
    userm = SQLUserManager(MyAuth, db_conn, user_class=MyUser)

    # for login/auth
    aa = AuthArch(userm, custom_templates_dir='auth', custom_reroutes={'login': 'dashboard'})
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
                password='hunter2'
            )
        userm.insert(u)

        u = userm.Content.create_default_with_form(
                email='user@test.d',
                username='tifa',
                role_id=2,
                password='asdasd'
            )
        userm.insert(u)

        userm.commit()


    projm = SQLContentManager(Project, db_conn)
    if not projm.table_exists:
        projm.create_table()

    def flash_error_and_redirect_to_select(rb, e):
        rb.flash(e.msg, 'err')
        return redirect(url_for('project.select'))

    ca_proj = CMSArch(projm, 'project', custom_templates_dir='projects',
            # in this case, this will let any failed delete attempts due to user error
            # to reroute to the select page
            # of course, we could always just create a delete.html under projects/ to not do this
            custom_callbacks={
                'delete': {
                    tags.USER_ERROR: flash_error_and_redirect_to_select
                }
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
            'role.update_self', # custom privilege for updating own role, see models.py
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

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))
        #return render_template('root.html')

    @app.route('/dashboard')
    @access_policies.login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/upload_test', methods=['GET', 'POST'])
    def upload_test():
        if request.method == 'POST':
            print(len(request.files.copy()))
            print(type(request.files.get('test_file')))
        return render_template('upload_test.html')

    transactionals.bootstrap(app, userm)

    return app
