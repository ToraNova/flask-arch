# this the shared class for most of the arch on flask-arch
# ported from vials project to flask-arch, 2022 feb 21
# author: toranova
# mailto: chia_jason96@live.com

from flask import Blueprint
from .blocks import RouteBlock
from .utils import ensure_type

def valid_override(keyword, cdict, strict_type):
    if keyword in cdict:
        ensure_type(cdict[keyword], strict_type, f'[{keyword}] = {cdict[keyword]}')
        return True
    return False

class Arch:

    def configure(self, keyword):
        if keyword not in self.route_blocks:
            raise KeyError('routeblock \'{keyword}\' cannot be configured because it does not exist.')
        return self.route_blocks[keyword]

    def add_route_blocks(self, rblist):
        for rb in rblist:
            self.add_route_block(rb)

    def add_route_block(self, rb, override=False):
        ensure_type(rb, RouteBlock, 'routeblock')
        if rb.keyword in self.route_blocks and not override:
            raise KeyError('routeblock \'{rb.keyword}\' already exists! set override=True to override.')
        self.route_blocks[rb.keyword] = rb

    def _debug(self):
        for rb in self.route_blocks.values():
            print(self.url_prefix)
            rb._debug()

    def init_app(self, app):

        for rb in self.route_blocks.values():
            if not isinstance(rb, RouteBlock):
                continue

            if rb.keyword in self.routes_disabled:
                continue

            # user overrides template
            if valid_override(rb.keyword, self.custom_templates, str):
                rb.template = self.custom_templates[rb.keyword]

            # user overrides reroute
            if valid_override(rb.keyword, self.custom_reroutes, str):
                rb.custom_reroute(self.custom_reroutes[rb.keyword])

            # user overrides reroute_kwargs
            if valid_override(rb.keyword, self.custom_reroutes_kwargs, dict):
                for argk, argv in self.custom_reroutes_kwargs[rb.keyword].items():
                    rb.reroute_kwargs[argk] = argv

            # user override custom_callbacks
            if valid_override(rb.keyword, self.custom_callbacks, dict):
                for tag, user_cb in self.custom_callbacks[rb.keyword].items():
                    if not callable(user_cb):
                        raise TypeError(f'custom_callbacks[\'{rb.keyword}\'][\'{tag}\'] not callable')
                    rb.callbacks[tag] = user_cb

            rb.finalize(self.name)
            self.bp.add_url_rule(rb.url_rule, rb.keyword, rb.view, **rb.options)

        app.register_blueprint(self.bp)
        #self._debug()  # enable for debugging

    def __init__(self, arch_name, custom_templates = {}, custom_reroutes = {}, custom_reroutes_kwargs = {}, custom_callbacks = {}, custom_url_prefix = None, routes_disabled=[]):
        '''
        arch_name - name of the architecture
        route_blocks - the route blocks to initialize and configure
        custom_templates, custom_reroutes, custom_reroutes_kwargs, custom_callbacks - user overrides
        url_prefix - url prefix of a blueprint generated. use / to have NO prefix, leave it at None to default to /<arch_name>
        '''

        ensure_type(arch_name, str, 'arch_name')
        ensure_type(custom_templates, dict, 'custom_templates')
        ensure_type(custom_reroutes, dict, 'custom_reroutes')
        ensure_type(custom_reroutes_kwargs, dict, 'custom_reroutes_kwargs')
        ensure_type(custom_callbacks, dict, 'custom_callbacks')
        ensure_type(custom_url_prefix, str, 'custom_url_prefix', allow_none=True)
        ensure_type(routes_disabled, list, 'routes_disabled')

        self.name = arch_name
        self.custom_templates = custom_templates.copy()
        self.custom_reroutes = custom_reroutes.copy()
        self.custom_reroutes_kwargs = custom_reroutes_kwargs.copy()
        self.custom_callbacks = custom_callbacks.copy()
        self.custom_url_prefix = custom_url_prefix
        self.routes_disabled = routes_disabled.copy()

        self.route_blocks = {}

        if self.custom_url_prefix is None:
            self.url_prefix = '/%s' % self.name
        elif self.custom_url_prefix == '/':
            self.url_prefix = None
        else:
            self.url_prefix = self.custom_url_prefix

        self.bp = Blueprint(self.name, __name__, url_prefix = self.url_prefix)
        self.blueprint = self.bp # alias
