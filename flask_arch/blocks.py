from .utils import ensure_type, ensure_callable

import traceback
from jinja2.exceptions import TemplateNotFound
from flask import redirect, url_for, flash, render_template, request, abort, current_app

# late-binding vs. early binding
# https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
def route_rewrap(wrap, routef):
    @wrap
    def f(*args):
        return routef(*args)
    return f


class RouteBlock:

    @property
    def default_url_rule(self):
        return f'/{self.keyword}'

    @property
    def default_methods(self):
        return ['GET']

    @property
    def default_access_policy(self):
        return None

    def set_custom_callback(self, tag, f):
        ensure_callable(f, 'custom_callback')
        self.callbacks[tag] = f

    # routeblock defines the default behavior
    def __init__(self, keyword, url_rule=None, template=None, reroute_to=None, reroute_external=False, reroute_kwargs={}, callbacks={}, access_policy=None, **options):
        # enforce typing
        ensure_type(keyword, str, 'keyword')
        if '.' in keyword:
            raise ValueError(f'keyword must not have dot (.) characters, not \'{keyword}\'')
        ensure_type(url_rule, str, 'url_rule', allow_none=True)
        ensure_type(template, str, 'template', allow_none=True)
        ensure_type(reroute_to, str, 'reroute', allow_none=True)
        ensure_type(reroute_external, bool, 'reroute_external')
        ensure_type(reroute_kwargs, dict, 'reroute_kwargs')
        ensure_type(callbacks, dict, 'callbacks')
        ensure_callable(access_policy, 'access_policy', allow_none=True)


        self.keyword = keyword
        self.url_rule = url_rule
        self.template = template
        self.reroute_to = reroute_to
        self.reroute_external = reroute_external
        self.reroute_kwargs = reroute_kwargs.copy()
        self.callbacks = callbacks.copy()
        self.access_policy = access_policy
        self.options = options

        if self.url_rule is None:
            self.url_rule = self.default_url_rule

        if self.template is None:
            self.template = f'{self.keyword}.html'

        if self.access_policy is None:
            self.access_policy = self.default_access_policy

        if 'methods' not in self.options:
            self.options['methods'] = self.default_methods


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

        return redirect(url_for(self.reroute_endpoint, **passd))

    def callback(self, tag, *args, **kwargs):
        if tag in self.callbacks and callable(self.callbacks[tag]):
            return self.callbacks[tag](self, *args, **kwargs)
        else:
            raise KeyError(f'custom callback for {self.keyword}.{tag} invalid')

    def finalize(self, arch_name):
        # called by the BaseArch init_app routines to ready up the block
        # ensure all configuration is done BEFORE this is called
        if not callable(self.view):
            raise NotImplementedError(f'{self.__class__.__name__} has no view method implemented.')

        if callable(self.access_policy):
            self.view = route_rewrap(self.access_policy, self.view)

        self._arch_name = arch_name

    @property
    def arch_name(self):
        return self._arch_name

    @property
    def reroute_endpoint(self):
        if self.reroute_to is None:
            raise ValueError(f'routeblock {self.__class__.__name__} has no reroute definitions')
        if '.' in self.reroute_to or self.reroute_external:
            # rerouting to external, as is
            return self.reroute_to
        else:
            # we need to append _arch_name as this is an implicit internal reroute
            return f'{self._arch_name}.{self.reroute_to}'

    def custom_reroute(self, r):
        self.reroute_external = True
        self.reroute_to = r

    def _debug(self):
        if hasattr(self, '_arch_name'):
            print(self._arch_name)
        else:
            print('unfinalized routeblock')
        print(self.keyword)
        print(self.template)
        try:
            print(self.reroute_endpoint)
        except ValueError:
            print('no reroute definition')
        print(self.reroute_kwargs)
        print(self.callbacks)
        print()

    def __str__(self):
        return self.keyword

    def __eq__(self, other):
        if isinstance(other, str):
            return self.keyword == other
        else:
            return self == other

    def client_error(self, e):
        if current_app.debug:
            traceback.print_exc()
            print('client_error', str(e))
        self.abort(400)

    def server_error(self, e):
        if current_app.debug:
            traceback.print_exc()
            raise e
        self.abort(500)

    def abort(self, code):
        abort(code)

    def flash(self, msg, cat = 'ok'):
        flash(msg, cat)

class RenderBlock(RouteBlock):

    def view(self):
        return self.render()

class RerouteBlock(RouteBlock):

    def view(self):
        return self.reroute()
