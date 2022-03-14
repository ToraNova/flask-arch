import jwt

from flask import Flask, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import current_user, login_required

from flask_arch.builtins import AuthArch, PasswordAuth
from flask_arch.user import ProcMemUserManager, SQLUserManager
from flask_arch.exceptions import UserError
from flask_arch.user import volatile, persist

from flask_arch.cms import SQLDBConnection

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr, declarative_base

class MyVolatileUser(volatile.procmem.User):

    def __init__(self, rp, actor):
        super().__init__(rp, actor)
        jd = jwt.decode(rp.form['jwt'], current_app.secret_key, algorithms=["HS256"])
        self.name = rp.form['username']
        self.email = jd['email']
        self.id = jd['email']

class MyPersistUser(persist.sql.User):
    userid = 'email'

    def __init__(self, rp, actor):
        super().__init__(rp, actor)
        jd = jwt.decode(rp.form['jwt'], current_app.secret_key, algorithms=["HS256"])
        self.email = jd['email']

    @declared_attr
    def email(cls):
        return Column(String(254),unique=True,nullable=False)


class MyPasswordAuth(PasswordAuth):

    @classmethod
    def parse_auth_data(cls, rp):
        email = rp.form['email']
        supplied_auth_data = rp.form['password']
        return email, supplied_auth_data

    @classmethod
    def parse_reset_data(cls, rp):
        # this is just one way, alternatively, data['email'] can also be used
        # the function is required for the user_manager to 'select' the right user
        # to perform password reset
        jd = jwt.decode(rp.form['jwt'], options={"verify_signature": False})
        identifier = jd['email']
        return identifier

    def reset(self, rp):
        # use the user's authentication data as the key to the jwt,
        # this effectively allows one-time password resets per password
        try:
            jd = jwt.decode(rp.form['jwt'], self.authd, algorithms=["HS256"])
        except Exception as e:
            raise UserError(401, 'invalid token')
        if jd['email'] != self.email:
            # we should never reach here
            raise UserError(401, 'email do not match')
        if rp.form['password_new'] != rp.form['password_confirm']:
            raise UserError(400, 'password do not match')

        self.set_auth_data(rp.form['password_confirm'])

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.config['DBURI'] = 'sqlite:///email_account.db' # specify database uri
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    if isinstance(test_config, dict) and test_config.get('PERSIST'):
        # use a volatile dictionary to handle user, users are ephemeral

        my_declarative_base = declarative_base()
        db_conn = SQLDBConnection(app.config['DBURI'], my_declarative_base)
        db_conn.configure_teardown(app)

        um = SQLUserManager(MyPasswordAuth, db_conn, user_class=MyPersistUser)

        if not um.table_exists:
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
