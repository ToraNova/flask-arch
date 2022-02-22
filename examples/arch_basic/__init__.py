# a simple flask-arch example
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_arch import BaseArch

class MyArch(BaseArch):
    def __init__(self,
            arch_name = 'default-myarch',
            templates = {},
            reroutes = {},
            reroutes_kwarg = {},
            custom_callbacks = {},
            url_prefix = None):

        super().__init__(arch_name, templates, reroutes, reroutes_kwarg, custom_callbacks, url_prefix)
        # this example arch has 2 routes
        self._default_tp('r1', 'r1.html') # default template for r1, if key r1 not set on templates
        self._default_tp('r2', 'r2.html') # default template for r2, if key r2 not set on templates
        self._default_rt('r2', f'{arch_name}.r2') # default reroute on r2, if key r2 not set on reroutes

        self._default_tp('missing', 'missing.html') # test what happens if template does not exist

    def init_app(self, app):

        @self.bp.route('/missing')
        def missing():
            return self.render()

        @self.bp.route('/r1')
        def r1():
            return self.render()

        @self.bp.route('/r2/<int:foo>', methods=['GET','POST'])
        def r2(foo):
            rscode = 200
            if request.method == 'POST':
                d = request.form.get('bar')
                password = request.form.get('password')
                if not d or not password:
                    flash('missing bar or password', 'err')
                    rscode = 402
                else:
                    if password != self._arch_name:
                        abort(401)

                    flash('post successful', 'ok')
                    return self.reroute(foo=foo)
            return self.render(display=foo), rscode

        app.register_blueprint(self.bp)


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
    ma2 = MyArch('myarch2', templates = {'r1': 'a2r1.html'}, reroutes = {'r2': 'myarch1.r2'})
    ma2.init_app(app)

    # of course you could use app like a normal flask app
    @app.route('/')
    def root():
        return render_template('root.html')

    return app
