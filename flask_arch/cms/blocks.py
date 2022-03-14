import os
from flask import request, send_file
from flask_login import current_user

from .base import ContentManager

from .. import exceptions, tags
from ..utils import ensure_type, ensure_callable, RequestParser
from ..blocks import RouteBlock

class ManageBlock(RouteBlock):

    def __init__(self, keyword, content_manager, **kwargs):
        super().__init__(keyword, **kwargs)
        ensure_type(content_manager, ContentManager, 'content_manager')
        self.content_manager = content_manager


class PrepExecBlock(ManageBlock):

    def __init__(self, keyword, content_manager, **kwargs):
        super().__init__(keyword, content_manager, **kwargs)
        ensure_callable(self.prepare, f'{self.__class__.__name__}.prepare')
        ensure_callable(self.execute, f'{self.__class__.__name__}.execute')

    def initial(self, rp):
        return self.render()

    @property
    def default_methods(self):
        return ['GET', 'POST']

    def view(self):
        rp = RequestParser(request)
        if rp.post_method:
            try:
                aargs = self.prepare(rp)
            except exceptions.UserError as e:
                return self.callback(tags.USER_ERROR, e)
            except Exception as e:
                # client error
                self.client_error(e)

            try:
                return self.execute(*aargs)
            except exceptions.UserError as e:
                return self.callback(tags.USER_ERROR, e) # handle user error
            except exceptions.IntegrityError as e:
                self.content_manager.rollback() # rollback
                return self.callback(tags.INTEGRITY_ERROR, e) # handle integrity error
            except Exception as e:
                # server error: unexpected exception
                self.content_manager.rollback() # rollback
                self.server_error(e)

        try:
            return self.initial(rp)
        except exceptions.UserError as e:
            return self.callback(tags.USER_ERROR, e)
        except Exception as e:
            # client error
            self.client_error(e)

class ContentLstBlock(ManageBlock):

    def view(self):
        c = self.content_manager.select_all()
        return self.render(data=c)

class ContentViewBlock(ManageBlock):

    def view(self):
        rp = RequestParser(request)
        c = self.content_manager.query(rp)
        return self.render(target=c)

class ContentFileBlock(ManageBlock):

    def view(self):
        rp = RequestParser(request)
        c = self.content_manager.query(rp)
        if not hasattr(c, 'get_store_dir'):
            self.abort(404)

        try:
            filename = self.content_manager.Content.parse_filename(rp)
            fp = c.read_file(filename)
        except Exception as e:
            # client error
            self.client_error(e)

        if fp is None:
            self.abort(404)
        return send_file(fp, download_name=filename)

class ContentAddBlock(PrepExecBlock):

    def initial(self, rp):
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


class ContentModBlock(PrepExecBlock):

    def initial(self, rp):
        c = self.content_manager.query(rp)
        return self.render(target=c)

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


class ContentDelBlock(PrepExecBlock):

    def initial(self, rp):
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
