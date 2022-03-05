import jwt
from flask import request, render_template, abort, current_app, url_for, flash

def bootstrap(app, um):

    # instead of going directly to register, user goes here first
    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
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
        return render_template('txnrq.html', txname="account creation")

    # password reset function
    @app.route('/reset_password', methods=['GET', 'POST'])
    def reset_password():
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
        return render_template('txnrq.html', txname="password reset")
