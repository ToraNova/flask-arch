# exports
from .base import Content as BaseContent
from .base import ContentManager as BaseContentManager
from .volatile import ContentManager as VolatileContentManager
from .sql import Content as SQLContent
from .sql import ContentManager as SQLContentManager

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declared_attr

from .. import BaseArch, RouteArch, callbacks, exceptions

def Arch(BaseArch):

    def __init__(self, content_manager, templates={}, reroutes={}, reroutes_kwarg={}, custom_callbacks={}, url_prefix=None, routes_disabled=[],):
        self.type_test(content_manager, BaseContentManager, 'content_manager')
        arch_name = content_manager.__contentname__

        SELECT_ALL  = 'select_all'
        SELECT_ONE  = 'select_one'
        INSERT      = 'insert'
        UPDATE      = 'update'
        DELETE      = 'delete'

        routing_rules = [
            RouteArch(SELECT_ALL, self.route_select_all),
            RouteArch(SELECT_ONE, self.route_select_one),
            RouteArch(INSERT,     self.route_insert),
            RouteArch(UPDATE,     self.route_update),
            RouteArch(DELETE,     self.route_delete),
        ]

        super().__init__(arch_name, templates, reroutes, reroutes_kwarg, custom_callbacks, url_prefix)

        self._type_test(routes_disabled, list, 'routes_disabled')
        self.content_manager = content_manager
        self._rdisable = routes_disabled

        self._default_tp('select_all', f'select_all.html')
        self._default_tp('select_one', f'select_one.html')
        self._default_tp('insert', f'insert.html')
        self._default_tp('update', f'update.html')
        self._default_tp('delete', f'delete.html')
