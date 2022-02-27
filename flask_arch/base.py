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

class BaseArch:

    def add_route(self, rb):
        self.bp.add_url_rule(rb.url_rule, rb.keyword, rb.view, **rb.options)

    def _debug(self):
        for rb in self.route_blocks:
            print(self.url_prefix)
            rb._debug()

    def init_app(self, app):
        for rb in self.route_blocks:
            rb.finalize(self.name)
            self.add_route(rb)
        app.register_blueprint(self.bp)
        #self._debug()  # enable for debugging

    def __init__(self, arch_name, route_blocks, custom_templates = {}, custom_reroutes = {}, custom_reroutes_kwargs = {}, custom_callbacks = {}, custom_url_prefix = None):
        '''
        arch_name - name of the architecture
        route_blocks - the route blocks to initialize and configure
        custom_templates, custom_reroutes, custom_reroutes_kwargs, custom_callbacks - user overrides
        url_prefix - url prefix of a blueprint generated. use / to have NO prefix, leave it at None to default to /<arch_name>
        '''

        ensure_type(arch_name, str, 'arch_name')
        ensure_type(route_blocks, list, 'route_blocks')
        ensure_type(custom_templates, dict, 'custom_templates')
        ensure_type(custom_reroutes, dict, 'custom_reroutes')
        ensure_type(custom_reroutes_kwargs, dict, 'custom_reroutes_kwargs')
        ensure_type(custom_callbacks, dict, 'custom_callbacks')
        ensure_type(custom_url_prefix, str, 'custom_url_prefix', allow_none=True)

        self.name = arch_name
        self.route_blocks = []

        for rb in route_blocks:
            if not isinstance(rb, RouteBlock):
                continue

            # user overrides template
            if valid_override(rb.keyword, custom_templates, str):
                rb.template = custom_templates[rb.keyword]

            # user overrides reroute
            if valid_override(rb.keyword, custom_reroutes, str):
                rb.reroute_to = custom_reroutes[rb.keyword]

            # user overrides reroute_kwargs
            if valid_override(rb.keyword, custom_reroutes_kwargs, dict):
                for argk, argv in custom_reroutes_kwargs[rb.keyword].items():
                    rb.reroute_kwargs[argk] = argv

            # user override custom_callbacks
            if valid_override(rb.keyword, custom_callbacks, dict):
                for tag, user_cb in custom_callbacks[rb.keyword].items():
                    if not callable(user_cb):
                        raise TypeError(f'custom_callbacks[\'{rb.keyword}\'][\'{tag}\'] not callable')
                    rb.callbacks[tag] = user_cb

            # add rb to route_blocks list
            self.route_blocks.append(rb)

        if custom_url_prefix is None:
            self.url_prefix = '/%s' % arch_name
        elif custom_url_prefix == '/':
            self.url_prefix = None
        else:
            self.url_prefix = custom_url_prefix

        self.bp = Blueprint(self.name, __name__, url_prefix = self.url_prefix)
