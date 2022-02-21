# basic login handler to work with flask-login

from flask_login import login_user, logout_user, current_user

class Basic:

    def login(self, arch, request):
        rscode = 200
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if not username or not password:
                arch.abort(400)

            if username in self.users and self.users[username].check_password(password):
                # using flask-login
                login_user(self.users[username])
                arch.flash('login success', 'ok')
                return arch.reroute()

            arch.flash('invalid credentials', 'err')
            rscode = 401
        return arch.render(), rscode

    def logout(self, arch, request):
        logout_user()
        arch.flash('logout success', 'ok')
        return arch.reroute()

    def update_user(self, user):
        self.users[user.name] = user

    def find_user_by_id(self, uid):
        for u in self.users.values():
            if uid == u.get_id():
                return u

    def __init__(self):
        self.users = {} # only for basic
