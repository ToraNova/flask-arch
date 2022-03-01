import jwt

from flask import Flask, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import current_user, login_required

from flask_arch.auth import AuthArch, PasswordAuth
from flask_arch.user import ProcMemUserManager, SQLUserManager
from flask_arch.exceptions import UserError
from flask_arch.user import volatile, persist

from flask_arch.cms import declarative_base, declared_attr, Column, String

class MyVolatileUser(volatile.procmem.User):
    userid = 'email'

class MyPersistUser(persist.sql.User):
    userid = 'email'

    @declared_attr
    def email(cls):
        return Column(String(254),unique=True,nullable=False)


class MyPasswordAuth(PasswordAuth):
    def __init__(self, email, username, password):
        super().__init__(email, password)
        self.name = username # username is extra, not used to identify the user

    @classmethod
    def parse_auth_data(cls, data):
        email = data['email']
        supplied_auth_data = data['password']
        return email, supplied_auth_data

    @classmethod
    def parse_reset_data(cls, data):
        # this is just one way, alternatively, data['email'] can also be used
        # the function is required for the user_manager to 'select' the right user
        # to perform password reset
        jd = jwt.decode(data['jwt'], options={"verify_signature": False})
        return jd['email']

    def reset(self, data):
        # use the user's authentication data as the key to the jwt,
        # this effectively allows one-time password resets per password
        try:
            jd = jwt.decode(data['jwt'], self.authd, algorithms=["HS256"])
        except Exception as e:
            raise UserError('invalid token', 401)
        if data['password_new'] != data['password_confirm']:
            raise UserError('password do not match', 400)
        if jd['email'] != self.email:
            # we should never reach here
            raise UserError('email do not match', 401)

        self.set_auth_data(data['password_confirm'])

    @classmethod
    def create(cls, data):
        if data['password'] != data['password_confirm']:
            raise UserError('password do not match', 400)
        # jwt is obtained from email verify request
        jd = jwt.decode(data['jwt'], current_app.secret_key, algorithms=["HS256"])
        nu = cls(jd['email'], data['username'], data['password'])
        return nu

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.config['DBURI'] = 'sqlite:///email_account.db' # specify database uri
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    if isinstance(test_config, dict) and test_config.get('PERSIST'):
        # use a volatile dictionary to handle user, users are ephemeral
        my_sql_declarative_base = declarative_base()
        um = SQLUserManager(MyPasswordAuth, app.config['DBURI'], user_class=MyPersistUser)

        if not um.table_exists():
            um.create_table()
    else:
        um = ProcMemUserManager(MyPasswordAuth, user_class=MyVolatileUser)

    auth_arch = AuthArch(um)

    # instead of going directly to register, user goes here first
    @app.route('/email_verify', methods=['GET', 'POST'])
    def email_verify():
        if request.method == 'POST':
            try:
                email = request.form['email']
            except Exception as e:
                print(e)
                abort(400)

            try:
                # send an email to the user
                token = jwt.encode({'email':email}, current_app.secret_key, algorithm='HS256')
                rediru = url_for('auth.register', token=token, _external=True)

                # simulate sending email on the browser itself
                # (THIS IS JUST AN EXAMPLE, ITS NOT HOW VERIFICATION WORKS!!!)
                return render_template('email/transaction.html', title='verify email', link=rediru)
            except Exception as e:
                print(e)
                abort(500)
        return render_template('get_email.html')

    # password reset function
    @app.route('/password_reset', methods=['GET', 'POST'])
    def password_reset():
        if request.method == 'POST':
            try:
                email = request.form['email']
            except Exception as e:
                print(e)
                abort(400)

            try:
                user = um.select_user(email)
                if user is None:
                    flash('invalid user', 'err')
                    return render_template('get_email.html')

                # send an email to the user, with the token containing the email,
                # using the user's current password hash as the secret key
                # this way, if the user has reset their password, the token is no longer valid
                token = jwt.encode({'email':email}, user.authd, algorithm='HS256')
                rediru = url_for('auth.reset', token=token, _external=True)

                # simulate sending email on the browser itself
                # (THIS IS JUST AN EXAMPLE, ITS NOT HOW VERIFICATION WORKS!!!)
                return render_template('email/transaction.html', title='password reset', link=rediru)
            except Exception as e:
                print(e)
                abort(500)
        return render_template('get_email.html')

    auth_arch.init_app(app)

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    return app
