# a simple flask-arch example
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_arch import BaseArch

from flask_arch.legacy import LegacyRouteBlock as RouteBlock

class MyArch(BaseArch):
    def __init__(self,
            arch_name = 'default-myarch',
            templates = {},
            reroutes = {},
            reroutes_kwarg = {},
            custom_callbacks = {},
            url_prefix = None):

        route_blocks = [
                RouteBlock('r1', lambda : self.render(),),
                RouteBlock('r2', self.r2_function, '/r2/<int:foo>', reroute='r2', methods=['GET', 'POST']),
                RouteBlock('rtest', lambda : self.reroute(), '/reroute-test', reroute='hi', reroute_external=True),
                RouteBlock('missing', lambda : self.render(), '/missing-template'),
                ]

        super().__init__(arch_name, route_blocks, templates, reroutes, reroutes_kwarg, custom_callbacks, url_prefix)

    def r2_function(self, foo):
        rscode = 200
        if request.method == 'POST':
            d = request.form.get('bar')
            password = request.form.get('password')
            if not d or not password:
                flash('missing bar or password', 'err')
                rscode = 402
            else:
                if password != self.name:
                    abort(401)

                flash('post successful', 'ok')
                return self.reroute(foo=foo)
        return self.render(display=foo), rscode

    def init_app(self, app):
        super().init_app(app)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    ma1 = MyArch('myarch1')
    ma1.init_app(app)

    # notice myarch2's r2 reroutes to myarch1's r2
    # it uses a different html template on r1
    ma2 = MyArch('myarch2', templates = {'r1': 'a2r1.html'}, reroutes = {'r2': 'myarch1.r2'}, reroutes_kwarg={'rtest':{'val':3}})
    ma2.init_app(app)

    # of course you could use app like a normal flask app
    @app.route('/')
    def root():
        return render_template('root.html')

    @app.route('/test/<string:val>')
    def hi(val):
        return val

    @app.route('/reroute_to_arch')
    def reroute_to_arch():
        return redirect(url_for('myarch1.r1'))

    return app
