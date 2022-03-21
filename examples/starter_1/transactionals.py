import jwt
from flask import request, render_template, abort, current_app, url_for, flash

def bootstrap(app, um):

    # instead of going directly to register, user goes here first
    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            try:
                identifier = request.form[um.Content.userid]
            except Exception as e:
                print(e)
                abort(400)

            try:
                token = jwt.encode(
                        {um.Content.userid:identifier},
                        current_app.secret_key,
                        algorithm='HS256'
                    )
                rediru = url_for('auth.register', token=token, _external=True)

                # simulate sending email on the browser itself
                # (THIS IS JUST AN EXAMPLE, ITS NOT HOW VERIFICATION WORKS!!!)
                return render_template('emails/transaction.html', title='verify email', link=rediru)
            except Exception as e:
                print(e)
                abort(500)
        return render_template('txnrq.html', txname="account creation")

    # password reset function
    @app.route('/reset_password', methods=['GET', 'POST'])
    def reset_password():
        if request.method == 'POST':
            try:
                identifier = request.form[um.Content.userid]
            except Exception as e:
                print(e)
                abort(400)

            try:
                user = um.select_user(identifier)
                if user is None:
                    flash('invalid user', 'err')
                    return render_template('txnrq.html')

                # using the user's current password hash as the secret key
                # this way, if the user has reset their password, the token is no longer valid
                token = jwt.encode(
                        {um.Content.userid:identifier},
                        user.authd,
                        algorithm='HS256')
                rediru = url_for('auth.reset', token=token, _external=True)

                # simulate sending email on the browser itself
                # (THIS IS JUST AN EXAMPLE, ITS NOT HOW VERIFICATION WORKS!!!)
                return render_template('emails/transaction.html', title='password reset', link=rediru)
            except Exception as e:
                print(e)
                abort(500)
        return render_template('txnrq.html', txname="password reset")
