# this the shared class for most of the arch on flask-arch
# ported from vials project to flask-arch, 2022 feb 21
# author: toranova
# mailto: chia_jason96@live.com

import traceback
from jinja2.exceptions import TemplateNotFound
from flask import Blueprint, redirect, url_for, flash, render_template, request, abort, current_app

from . import tags

class RouteArch:
    def __init__(self, keyword, view_function, reroute=None, **options):
        self.keyword = keyword
        self.template = f'{keyword}.html' # default template are 'keyword.html'
        self.reroute = reroute
        if isinstance(reroute, str):
            self.reroute_absolute = '.' in reroute
        self.options = options
        self.view_function = view_function

    def __str__(self):
        return self.keyword

    def __lt__(self, other):
        return self.keyword < other.keyword

    def __gt__(self, other):
        return self.keyword > other.keyword

    def __eq__(self, other):
        return self.keyword == other.keyword

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
            passd = {}
            for k, v in self._rkarg.get(route_key).items():
                if v is None and k in kwargs:
                    passd[k] = kwargs[k]
                else:
                    passd[k] = v
            return redirect(url_for(self._route[route_key], **passd))
        return redirect(url_for(self._route[route_key], **kwargs))

    def custom(self, tag, *args, **kwargs):
        route_key = self.get_route_key()
        if not self.callback_valid(route_key, tag):
            raise KeyError(f'custom callback for {route_key}.{tag} invalid')
        return self._ccall[route_key][tag](self, *args, **kwargs)

    # default functions for flask-arch project dev
    def default_tp(self, route_key, default):
        if not self._templ.get(route_key):
            self._templ[route_key] = default

    def default_rt(self, route_key, default):
        if not self._route.get(route_key):
            self._route[route_key] = default

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

    def default_cb(self, route_key, tag, default):
        if not self.callback_valid(route_key, tag):
            if not callable(default):
                raise TypeError(f'default arg for callback on {route_key}.{tag} should be callable')
            self._ccall[route_key][tag] = default

    # for flask_arch.cms, where reference 'content' is always needed
    # deprecated, kept for backward compatibility,
    # use _reroute_mod instead
    # use: call _reroute_mod('name', 'value') after reroute settings
    # to always insert url_for(... , name = value , ...) in reroute calls
    def _reroute_mod(self, farg_name, farg_value):
        for k in self._route.keys():
            if self._rkarg.get(k) is None:
                self._rkarg[k] = {farg_name: farg_value}
            else:
                self._rkarg[k][farg_name] = farg_value

    def type_test(self, arg, typ, argn, allow_none = False):
        if not isinstance(arg, typ):
            if allow_none and arg is None:
                return
            raise TypeError(f'{argn} should be of instance {typ}, got {type(arg)}')

    def add_route(self, ra):
        rule = f'/{ra.keyword}'
        self.bp.add_url_rule(rule, ra.keyword, ra.view_function, **ra.options)

    def init_app(self, app):
        for ra in self.routing_rules:
            self.add_route(ra)
        app.register_blueprint(self.bp)

    # arch_name - name of the arch
    # templates - the template dictionary, same for reroutes
    # reroutes_kwarg - additional kwarg to pass in during a reroute fcall
    # rex_callback - route execution callback, a function table at the end of a route execution
    # url_prefix - url prefix of a blueprint generated. use / to have NO prefix, leave it at None to default to /<arch_name>
    def __init__(self, arch_name, routing_rules, templates = {}, reroutes = {}, reroutes_kwarg = {}, custom_callbacks = {}, url_prefix = None):
        self.type_test(arch_name, str, 'arch_name')
        self.type_test(templates, dict, 'templates')
        self.type_test(reroutes, dict, 'reroutes')
        self.type_test(reroutes_kwarg, dict, 'reroutes_kwarg')
        self.type_test(custom_callbacks, dict, 'custom_callbacks')
        self.type_test(url_prefix, str, 'url_prefix', allow_none=True)
        self._templ = templates.copy()
        self._route = reroutes.copy()
        self._rkarg = reroutes_kwarg.copy()
        self._ccall = custom_callbacks.copy()

        if url_prefix is None:
            self._url_prefix = '/%s' % arch_name
        elif url_prefix == '/':
            self._url_prefix = None
        else:
            self._url_prefix = url_prefix
        self._arch_name = arch_name

        self.type_test(routing_rules, list, 'routing_rules')
        self.routing_rules = []
        for ra in routing_rules:
            if ra is None:
                continue
            if isinstance(ra.template, str):
                self.default_tp(ra.keyword, ra.template)
            if isinstance(ra.reroute, str):
                if ra.reroute_absolute:
                    self.default_rt(ra.keyword, ra.reroute)
                else:
                    self.default_rt(ra.keyword, f'{self._arch_name}.{ra.reroute}')
            self.routing_rules.append(ra)

        self.bp = Blueprint(self._arch_name, __name__, url_prefix = self._url_prefix)

    def _debug(self):
        print(self._arch_name)
        print(self._templ)
        print(self._route)
        print(self._rkarg)
        print(self._ccall)
        print()
