from flask import Flask, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import current_user, login_required

from flask_arch.auth import AdminAuthArch, PasswordAuth, privileges, access_policies
from flask_arch.user import ProcMemUserManager, SQLUserManager, BaseRole, no_role
from flask_arch.exceptions import UserError
from flask_arch.user import volatile, persist
from flask_arch.utils import parse_boolean

from flask_arch.cms import declarative_base, declared_attr, Column, String

admin_role = BaseRole('admin', [privileges.USERSEL, privileges.USERADD, privileges.USERMOD, privileges.USERDEL])
paid_role = BaseRole('premium', ['select.treasure'])

class VolatileManagedUser(volatile.procmem.User):

    def generate_form_data(self):
        return [admin_role, paid_role, no_role]

    @classmethod
    def create(cls, data):
        # created by an admin
        if data['password'] != data['password_confirm']:
            raise UserError('password do not match', 400)
        nu = cls(data['username'], data['password'])

        if parse_boolean(data, 'premium_user'):
            nu.role = paid_role

        return nu

    def update(self, data):
        # updated by an admin

        trole = data['role']
        if trole == 'admin':
            self.role = admin_role
        elif trole == 'premium':
            self.role = paid_role
        else:
            self.role = no_role

    def delete(self, data):
        # deleted by an admin
        pass

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.config['DBURI'] = 'sqlite:///admin_account.db' # specify database uri
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)


    if isinstance(test_config, dict) and test_config.get('PERSIST'):
        # use a volatile dictionary to handle user, users are ephemeral
        my_sql_declarative_base = declarative_base()
        um = SQLUserManager(PasswordAuth, app.config['DBURI'])

        if not um.table_exists():
            um.create_table()
    else:
        um = ProcMemUserManager(PasswordAuth, user_class=VolatileManagedUser)

        u = um.construct('jason', 'hunter2')
        u.role = admin_role
        um.insert(u)

        u = um.construct('john', 'asd')
        u.role = paid_role
        um.insert(u)

        u = um.construct('james', 'test')
        um.insert(u)

    auth_arch = AdminAuthArch(um)

    auth_arch.init_app(app)

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    @app.route('/treasure')
    @access_policies.privilege_required('select.treasure')
    def treasure():
        return 'secret'

    return app
