# this the shared class for most of the arch on flask-arch
# ported from vials project to flask-arch, 2022 feb 21
# author: toranova
# mailto: chia_jason96@live.com

from flask import Blueprint, redirect, url_for, flash, render_template, request, abort

class BaseArch:

    def get_view_name():
        vn = request.endpoint.split('.')[-1]
        return vn

    def abort(self, code):
        abort(code)

    def flash(self, msg, cat):
        flash(msg, cat)

    def render(self, **kwargs):
        route_key = BaseArch.get_view_name()
        return self._render(route_key, **kwargs)

    def _render(self, route_key, **kwargs):
        return render_template(self._templ[route_key], **kwargs)

    def reroute(self, **kwargs):
        route_key = BaseArch.get_view_name()
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
        route_key = BaseArch.get_view_name()
        if not self.__callback_valid(route_key, tag):
            raise KeyError(f'custom callback for {route_key}.{tag} invalid')
        return self._ccall[route_key][tag](*args, **kwargs)

    # default functions for flask-arch project dev
    def _default_tp(self, route_key, default):
        if not self._templ.get(route_key):
            self._templ[route_key] = default

    def _default_rt(self, route_key, default):
        if not self._route.get(route_key):
            self._route[route_key] = default

    def __callback_valid(self, route_key, tag):
        if not route_key in self._ccall:
            return False
        elif not isinstance(self._ccall[route_key], dict):
            return False
        elif not tag in self._ccall[route_key]:
            return False
        elif not callable(self._ccall[route_key][tag]):
            return False
        return True

    def _default_cb(self, route_key, tag, default):
        if not self.__callback_valid(route_key, tag):
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

    def _type_test(self, arg, typ, argn, allow_none = False):
        if not isinstance(arg, typ):
            if allow_none and arg is None:
                return
            raise TypeError(f'{argn} should be of instance {typ}, got {type(arg)}')

    # arch_name - name of the arch
    # templates - the template dictionary, same for reroutes
    # reroutes_kwarg - additional kwarg to pass in during a reroute fcall
    # rex_callback - route execution callback, a function table at the end of a route execution
    # url_prefix - url prefix of a blueprint generated. use / to have NO prefix, leave it at None to default to /<arch_name>
    def __init__(self, arch_name, templates = {}, reroutes = {}, reroutes_kwarg = {}, custom_callbacks = {}, url_prefix = None):
        self._type_test(arch_name, str, 'arch_name')
        self._type_test(templates, dict, 'templates')
        self._type_test(reroutes, dict, 'reroutes')
        self._type_test(reroutes_kwarg, dict, 'reroutes_kwarg')
        self._type_test(custom_callbacks, dict, 'custom_callbacks')
        self._type_test(url_prefix, str, 'url_prefix', allow_none=True)
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

        self.bp = Blueprint(self._arch_name, __name__, url_prefix = self._url_prefix)
