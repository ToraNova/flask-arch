
from flask import request
from flask_login import current_user

from .base import ContentManager
from .. import exceptions, tags
from ..utils import ensure_type, ensure_callable
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

    def initial(self):
        return self.render()

    @property
    def default_methods(self):
        return ['GET', 'POST']

    def view(self):
        if request.method == 'POST':
            try:
                aargs = self.prepare()
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
            return self.initial()
        except exceptions.UserError as e:
            return self.callback(tags.USER_ERROR, e)
        except Exception as e:
            # client error
            self.client_error(e)

class ContentLstBlock(ManageBlock):

    def view(self):
        c = self.content_manager.select_all()
        return self.render(data=c)


class ContentAddBlock(PrepExecBlock):

    def initial(self):
        c = self.content_manager.content_class
        return self.render(target_class=c)

    def prepare(self):
        c = self.content_manager.create(request.form.copy(), current_user)
        return (c,)

    def execute(self, target):
        # insert new user
        identifier = self.content_manager.insert(target)
        self.content_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()


class ContentModBlock(PrepExecBlock):

    def initial(self):
        c = self.content_manager.query(request.args.copy())
        return self.render(target=c)

    def prepare(self):
        c = self.content_manager.modify(request.args.copy(), request.form.copy(), current_user)
        return (c,)

    def execute(self, target):
        # insert new user
        identifier = self.content_manager.update(target)
        self.content_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()


class ContentDelBlock(PrepExecBlock):

    def initial(self):
        c = self.content_manager.query(request.args.copy())
        return self.render(target=c)

    def prepare(self):
        c = self.content_manager.query(request.args.copy())
        return (c,)

    def execute(self, target):
        # insert new user
        identifier = self.content_manager.delete(target)
        self.content_manager.commit() # commit insertion
        self.callback(tags.SUCCESS, identifier)
        return self.reroute()
