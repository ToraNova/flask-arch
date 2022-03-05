from flask import Flask, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import current_user, login_required

from flask_arch.builtins import AuthArch, UserManageArch, PasswordAuth, privileges
from flask_arch.user import ProcMemUser, ProcMemUserManager, BaseRole, access_policies, no_role
from flask_arch.exceptions import UserError
from flask_arch.utils import parse_boolean

admin_role = BaseRole('admin', [privileges.USERSEL, privileges.USERADD, privileges.USERMOD, privileges.USERDEL])
paid_role = BaseRole('premium', ['select.treasure'])

class VolatileManagedUser(ProcMemUser):

    # these are up to the implementation
    # create (useradd) will pass in the class
    @classmethod
    def get_user_roles(cls):
        return [admin_role, paid_role, no_role]

    # while update (usermod) will pass in the user obj
    # they may hve different response, but in this case they are the same
    def get_own_roles(self):
        return [admin_role, paid_role, no_role]

    @classmethod
    def create(cls, data):
        # created by an admin
        if data['password'] != data['password_confirm']:
            raise UserError('password do not match', 400)
        nu = cls(data['username'], data['password'])

        trole = data['role']
        if trole == 'admin':
            nu.role = admin_role
        elif trole == 'premium':
            nu.role = paid_role
        else:
            nu.role = no_role

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
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    userman = ProcMemUserManager(PasswordAuth, user_class=VolatileManagedUser)

    u = userman.construct('jason', 'hunter2')
    u.role = admin_role
    userman.insert(u)

    u = userman.construct('john', 'asd')
    u.role = paid_role
    userman.insert(u)

    u = userman.construct('james', 'test')
    userman.insert(u)

    # for login
    auth_arch = AuthArch(userman)
    auth_arch.init_app(app)

    # for user manag
    userman_arch = UserManageArch(userman)
    userman_arch.init_app(app)

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    @app.route('/treasure')
    @access_policies.privilege_required('select.treasure')
    def treasure():
        return 'secret'

    @app.route('/admin_only')
    @access_policies.rolename_required('admin')
    def admin_only():
        return 'you can see this because you are an admin'

    return app
