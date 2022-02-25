
import traceback
from jinja2.exceptions import TemplateNotFound
from flask import redirect, url_for, flash, render_template, request, abort, current_app

class RouteBlock:

    def client_error(self, e):
        if current_app.debug:
            print('client_error', str(e))
        self.abort(400)

    def server_error(self, e):
        if current_app.debug:
            traceback.print_exc()
            raise e
        self.abort(500)

    def init_bp_name(self, bp_name):
        if not callable(self.view):
            raise NotImplementedError(f'{self.__class__.__name__} has no view method implemented.')
        self._bp_name = bp_name

    def _debug(self):
        print(self._bp_name)
        print(self.keyword)
        print(self.template)
        print(self.reroute)
        print(self.reroute_kwargs)
        print(self.custom_callbacks)
        print()

    def render(self, **kwargs):
        try:
            return render_template(self.template, **kwargs)
        except TemplateNotFound:
            return f'template for {self.keyword}: \'{self.template}\' not found.', 500

    def reroute(self, **kwargs):
        # reroute action
        passd = kwargs
        if isinstance(self.reroute_kwargs, dict):
            for k, v in self.reroute_kwargs.items():
                passd[k] = v
        return redirect(url_for(self._get_reroute_endpoint, **passd))

    def custom(self, tag, *args, **kwargs):
        route_key = self.get_route_key()
        if tag in self.custom_callbacks and callable(self.custom_callbacks[tag]):
            return self.custom_callbacks(self, *args, **kwargs)
        else:
            raise KeyError(f'custom callback for {self.keyword}.{tag} invalid')

    def abort(self, code):
        abort(code)

    def flash(self, msg, cat = 'ok'):
        flash(msg, cat)

    def _get_reroute_endpoint(self):
        if '.' in self.reroute or self.reroute_external:
            return self.reroute
        else:
            f'{self._bp_name}.{self.reroute}'

    # routeblock defines the default behavior
    def __init__(self, keyword, url_rule=None, reroute=None, reroute_external=False, **options):
        if not isinstance(keyword, str):
            raise TypeError(f'keyword must be an instance of str, not {type(keyword)}')
        if '.' in keyword:
            raise ValueError(f'keyword must not have dot (.) characters, not \'{keyword}\'')
        self.keyword = keyword  # keyword of the route
        if isinstance(url_rule, str):
            self.url_rule = url_rule
        else:
            self.url_rule = f'/{self.keyword}'
        self.template = f'{keyword}.html'  # default template is always '<keyword>.html'
        self.reroute = reroute  # the reroute path
        self.reroute_external = reroute_external
        self.options = options  # options when adding url
        self.reroute_kwargs = {}
        self.custom_callbacks = {}

    def __str__(self):
        return self.keyword

    def __eq__(self, other):
        return self.keyword == other.keyword

