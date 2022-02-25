# this the shared class for most of the arch on flask-arch
# ported from vials project to flask-arch, 2022 feb 21
# author: toranova
# mailto: chia_jason96@live.com

import traceback
from jinja2.exceptions import TemplateNotFound
from flask import Blueprint, redirect, url_for, flash, render_template, request, abort, current_app

from . import tags
from .blocks import RouteBlock
from .legacy import LegacyRouteBlock

class BaseArch:

    def client_error(self, e):
        if current_app.debug:
            print('client_error', str(e))
        self.abort(400)

    def server_error(self, e):
        if current_app.debug:
            traceback.print_exc()
            raise e
        self.abort(500)

    def get_route_key(self):
        vn = request.endpoint.split('.')[-1]
        return vn

    def abort(self, code):
        abort(code)

    def flash(self, msg, cat = 'ok'):
        flash(msg, cat)

    def render(self, **kwargs):
        route_key = self.get_route_key()
        return self._render(route_key, **kwargs)

    def _render(self, route_key, **kwargs):
        try:
            return render_template(self._templ[route_key], **kwargs)
        except TemplateNotFound:
            return f'template for {route_key}: \'{self._templ.get(route_key)}\' not found.', 500

    def reroute(self, **kwargs):
        route_key = self.get_route_key()
        # reroute action
        if isinstance(self._rkarg.get(route_key), dict):
            passd = kwargs
            for k, v in self._rkarg.get(route_key).items():
                passd[k] = v
            return redirect(url_for(self._route[route_key], **passd))
        return redirect(url_for(self._route[route_key], **kwargs))

    def custom(self, tag, *args, **kwargs):
        route_key = self.get_route_key()
        if not self.callback_valid(route_key, tag):
            raise KeyError(f'custom callback for {route_key}.{tag} invalid')
        return self._ccall[route_key][tag](self, *args, **kwargs)

    def callback_valid(self, route_key, tag):
        if not route_key in self._ccall:
            self._ccall[route_key] = {}
            return False
        elif not isinstance(self._ccall[route_key], dict):
            return False
        elif not tag in self._ccall[route_key]:
            return False
        elif not callable(self._ccall[route_key][tag]):
            return False
        return True

    # default functions for flask-arch project dev
    def default_tp(self, route_key, default):
        if not self._templ.get(route_key):
            self._templ[route_key] = default

    def default_rt(self, route_key, default):
        if not self._route.get(route_key):
            self._route[route_key] = default

    def default_cb(self, route_key, tag, default):
        if not self.callback_valid(route_key, tag):
            if not callable(default):
                raise TypeError(f'default arg for callback on {route_key}.{tag} should be callable')
            self._ccall[route_key][tag] = default

    def type_test(self, arg, typ, argn, allow_none = False):
        if not isinstance(arg, typ):
            if allow_none and arg is None:
                return
            raise TypeError(f'{argn} should be of instance {typ}, got {type(arg)}')

    def add_route(self, rb):
        if isinstance(rb, LegacyRouteBlock):
            self.bp.add_url_rule(rb.url_rule, rb.keyword, rb.view_function, **rb.options)
        else:
            self.bp.add_url_rule(rb.url_rule, rb.keyword, rb.view, **rb.options)

    def init_app(self, app):
        for rb in self.route_blocks:
            self.add_route(rb)
        app.register_blueprint(self.bp)

    def valid_override(self, keyword, cdict, strict_type):
        if keyword in cdict:
            self.type_test(cdict[keyword], strict_type, f'[{keyword}] = {cdict[keyword]}')
            return True
        return False

    # arch_name - name of the arch
    # templates - the template dictionary, same for reroutes
    # reroutes_kwarg - additional kwarg to pass in during a reroute fcall
    # rex_callback - route execution callback, a function table at the end of a route execution
    # url_prefix - url prefix of a blueprint generated. use / to have NO prefix, leave it at None to default to /<arch_name>
    def __init__(self, arch_name, route_blocks, templates = {}, reroutes = {}, reroutes_kwargs = {}, custom_callbacks = {}, url_prefix = None):

        self.type_test(arch_name, str, 'arch_name')
        self.type_test(route_blocks, list, 'route_blocks')
        self.type_test(templates, dict, 'templates')
        self.type_test(reroutes, dict, 'reroutes')
        self.type_test(reroutes_kwargs, dict, 'reroutes_kwargs')
        self.type_test(custom_callbacks, dict, 'custom_callbacks')
        self.type_test(url_prefix, str, 'url_prefix', allow_none=True)

        self.name = arch_name
        self.route_blocks = []
        self._templ = {}
        self._route = {}
        self._rkarg = {}
        self._ccall = {}

        for rb in route_blocks:
            if not isinstance(rb, RouteBlock) and not isinstance(rb, LegacyRouteBlock):
                continue

            if self.valid_override(rb.keyword, templates, str):
                rb.template = templates[rb.keyword]

            if self.valid_override(rb.keyword, reroutes, str):
                rb.reroute = reroutes[rb.keyword]

            if self.valid_override(rb.keyword, reroutes_kwargs, dict):
                for k, v in reroutes_kwargs[rb.keyword].items():
                    rb.reroute_kwargs[k] = v

            if self.valid_override(rb.keyword, custom_callbacks, dict):
                for k, v in custom_callbacks[rb.keyword].items():
                    if not callable(v):
                        raise TypeError(f'custom_callbacks[\'{rb.keyword}\'][\'{k}\'] not callable')
                    rb.custom_callbacks[k] = v

            self._templ[rb.keyword] = rb.template
            if isinstance(rb.reroute, str):
                if '.' in rb.reroute or rb.reroute_external:
                    self._route[rb.keyword] = rb.reroute
                else:
                    self._route[rb.keyword] = f'{self.name}.{rb.reroute}'
            self._rkarg[rb.keyword] = rb.reroute_kwargs
            self._ccall[rb.keyword] = rb.custom_callbacks

            rb.init_bp_name(self.name)
            self.route_blocks.append(rb)

        if url_prefix is None:
            self._url_prefix = '/%s' % arch_name
        elif url_prefix == '/':
            self._url_prefix = None
        else:
            self._url_prefix = url_prefix
        self.bp = Blueprint(self.name, __name__, url_prefix = self._url_prefix)
        self._debug()

    def _debug(self):
        for rb in self.route_blocks:
            rb._debug()
