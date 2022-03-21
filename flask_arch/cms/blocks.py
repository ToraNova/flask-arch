import os
from flask import request, send_file
from flask_login import current_user

from .base import ContentManager

from .. import tags
from ..utils import ensure_type, ensure_callable, RequestParser
from ..blocks import RouteBlock

class ManageBlock(RouteBlock):

    def __init__(self, keyword, content_manager, **kwargs):
        super().__init__(keyword, **kwargs)
        ensure_type(content_manager, ContentManager, 'content_manager')
        self.content_manager = content_manager

class LstBlock(ManageBlock):

    def route(self):
        try:
            c = self.content_manager.select_all()
            return self.render(data=c)
        except Exception as e:
            # likely a server error
            return self.server_error(e)

class ViewBlock(ManageBlock):

    def prepare_target(self, rp):
        c = self.content_manager.query(rp)
        cv = c.view(rp, current_user)
        return cv

    def route(self):
        try:
            rp = RequestParser(request)
            cv = self.prepare_target(rp)
            return self.render(target=cv)
        except Exception as e:
            # likely a client error
            e.reroute = True # specify that the fallback will be a reroute
            # this is because, the render has failed!
            return self.client_error(e)

class FileBlock(ViewBlock):

    def route(self):
        if not hasattr(self.content_manager.Content, 'read_file'):
            self.abort(404)

        try:
            rp = RequestParser(request)
            target = self.prepare_target(rp)
            filename = self.content_manager.Content.parse_filename(rp)
            fp = target.read_file(filename)

            return send_file(fp, download_name=filename)
        except Exception as e:
            return self.client_error(e)


class PrepExecBlock(ManageBlock):

    def __init__(self, keyword, content_manager, **kwargs):
        super().__init__(keyword, content_manager, **kwargs)
        ensure_callable(self.prepare, f'{self.__class__.__name__}.prepare')
        ensure_callable(self.execute, f'{self.__class__.__name__}.execute')

    def initial(self):
        return self.render()

    @property
    def default_methods(self):
        return ['GET', 'POST']

    def route(self):
        if request.method == 'POST':
            rp = RequestParser(request)
            try:
                aargs = self.prepare(rp)
            except Exception as e:
                # client error
                return self.client_error(e)

            try:
                return self.execute(*aargs)
            except Exception as e:
                # server error: unexpected exception
                self.content_manager.rollback() # rollback
                return self.server_error(e)

        try:
            return self.initial()
        except Exception as e:
            # client error
            e.reroute = True # the render/initial request likely failed. reroute is necessary
            return self.client_error(e)

class AddBlock(PrepExecBlock):

    def initial(self):
        c = self.content_manager.Content
        return self.render(Content=c)

    def prepare(self, rp):
        c = self.content_manager.Content(rp, current_user)
        c.before_insert(rp, current_user) # before commiting the insert
        return (rp, c)

    def execute(self, rp, c):
        # insert new user
        self.content_manager.insert(c)
        self.content_manager.commit() # commit insertion
        c.after_insert(rp, current_user)
        self.callback(tags.SUCCESS, c.id)
        return self.reroute()


class ModBlock(PrepExecBlock):

    def initial(self):
        rp = RequestParser(request)
        c = self.content_manager.query(rp)
        cv = c.view(rp, current_user)
        return self.render(target=cv)

    def prepare(self, rp):
        c = self.content_manager.query(rp)
        c.modify(rp, current_user)
        c.before_update(rp, current_user)
        return (rp, c)

    def execute(self, rp, c):
        # insert new user
        self.content_manager.update(c)
        self.content_manager.commit() # commit insertion
        c.after_update(rp, current_user)
        self.callback(tags.SUCCESS, c.id)
        return self.reroute()


class DelBlock(PrepExecBlock):

    def initial(self):
        rp = RequestParser(request)
        c = self.content_manager.query(rp)
        return self.render(target=c)

    def prepare(self, rp):
        c = self.content_manager.query(rp)
        c.deinit(rp, current_user)
        c.before_delete(rp, current_user)
        return (rp, c)

    def execute(self, rp, c):
        # insert new user
        self.content_manager.delete(c)
        self.content_manager.commit() # commit insertion
        c.after_delete(rp, current_user)
        self.callback(tags.SUCCESS, c.id)
        return self.reroute()
