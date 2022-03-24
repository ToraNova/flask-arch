from flask import Flask, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import current_user, login_required

from flask_arch import tags
from flask_arch.builtins import AuthArch, UserManageArch, PasswordAuth
from flask_arch.user import ProcMemUser, ProcMemUserManager, BaseRole, access_policies, no_role
from flask_arch.exceptions import UserError
from flask_arch.utils import parse_boolean

admin_role = BaseRole.create_default_with_form(name='admin')
admin_role.set_list_privileges(
        ['user.view', 'user.add', 'user.mod', 'user.del']
)
paid_role = BaseRole.create_default_with_form(name='premium')
paid_role.set_list_privileges(
        ['my_privilege']
)

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

    def set_role(self, role):
        if role == 'admin':
            self.role = admin_role
        elif role == 'premium':
            self.role = paid_role
        else:
            self.role = no_role

    def __init__(self, rp, actor):
        super().__init__(rp, actor)
        self.role = no_role

        if actor != self:
            # user is being updated by another user (probably an admin)
            if rp.form.get('role'):
                self.set_role(rp.form['role'])

    def modify(self, rp, actor):
        super().modify(rp, actor)

        if actor != self:
            # user is being updated by another user (probably an admin)
            if rp.form.get('role'):
                self.set_role(rp.form['role'])

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    userman = ProcMemUserManager(PasswordAuth, user_class=VolatileManagedUser)

    u = userman.Content.create_default_with_form(username='jason', password='hunter2', password_confirm='hunter2')
    u.role = admin_role
    userman.insert(u)

    u = userman.Content.create_default_with_form(username='john', password='asd', password_confirm='asd')
    u.role = paid_role
    userman.insert(u)

    u = userman.Content.create_default_with_form(username='james', password='test', password_confirm='test')
    userman.insert(u)

    # for login
    auth_arch = AuthArch(userman)
    auth_arch.init_app(app)

    # for user manag
    userman_arch = UserManageArch(userman, custom_callbacks={
        'add':{
            tags.SUCCESS: lambda rb, e: rb.flash(f'useradd successful', 'ok')
            },
        'mod':{
            tags.SUCCESS: lambda rb, e: rb.flash(f'usermod successful', 'ok')
            },
        'del':{
            tags.SUCCESS: lambda rb, e: rb.flash(f'userdel successful', 'ok')
            }
        })
    userman_arch.init_app(app)

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    @app.route('/treasure')
    @access_policies.privilege_required('my_privilege')
    def treasure():
        return 'secret'

    @app.route('/admin_only')
    @access_policies.rolename_required('admin')
    def admin_only():
        return 'you can see this because you are an admin'

    return app
