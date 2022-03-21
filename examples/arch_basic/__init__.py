# a simple flask-arch example
from flask import Flask, request, render_template, redirect, url_for, flash, abort

from flask_arch import BaseArch, RouteBlock
from flask_arch.blocks import RenderBlock, RerouteBlock

#from flask_arch.legacy import LegacyRouteBlock as RouteBlock

class MyBlock(RouteBlock):

    @property
    def default_url_rule(self):
        return f'/{self.keyword}/<int:foo>'

    def route(self, foo):
        rscode = 200
        if request.method == 'POST':
            d = request.form.get('bar')
            password = request.form.get('password')
            if not d or not password:
                flash('missing bar or password', 'err')
                rscode = 402
            else:
                if password != self.arch_name:
                    abort(401)

                flash('post successful', 'ok')
                return self.reroute(foo=foo)
        return self.render(display=foo), rscode


class MyArch(BaseArch):
    def __init__(self, arch_name='default-myarch', **custom_options):
        super().__init__(arch_name, **custom_options)

        rblist = [
            RenderBlock('r1'),
            MyBlock('r2', reroute_to='r2', methods=['GET', 'POST']),
            RerouteBlock('rtest', '/reroute-test', reroute_to='hi', reroute_external=True),
            RenderBlock('missing', '/missing-template'),
        ]

        self.add_route_blocks(rblist)

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
    ma2 = MyArch('myarch2',
        custom_templates = {'r1': 'a2r1.html'},
        custom_reroutes = {'r2': 'myarch1.r2'},
        custom_reroutes_kwargs={'rtest':{'val':3}}
    )
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
