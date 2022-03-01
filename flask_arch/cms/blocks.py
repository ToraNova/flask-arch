
from flask import request

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

        return self.render()
