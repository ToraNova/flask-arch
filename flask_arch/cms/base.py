# base object for the content management system
# this system also handles user
import datetime
from ..utils import RequestParser

class Content:
    '''ancestor of all content managed by a ContentManager'''

    id = None

    def view(self, rp, actor):
        # can be overwritten to only allow certain actors to view the content
        return self

    def __init__(self, rp, actor):
        # user must define the creation behavior
        raise NotImplementedError(f'__init__(self, rp, actor) on {self.__class__.__name__} not implemented.')

    def before_insert(self, rp, actor):
        # called before commit
        # set creator_id
        if isinstance(actor, Content):
            self.creator_id = actor.id
        self.created_on = datetime.datetime.now()

    def after_insert(self, rp, actor):
        # called after commit
        pass

    def modify(self, rp, actor):
        # user must define the modification behavior
        raise NotImplementedError(f'update(self, rp, actor) on {self.__class__.__name__} not implemented.')

    def before_update(self, rp, actor):
        # called before commit
        if isinstance(actor, Content):
            self.modifier_id = actor.id
        self.updated_on = datetime.datetime.now()

    def after_update(self, rp, actor):
        # called after commit
        pass

    def deinit(self, rp, actor):
        # deinitialization behavior
        pass

    def before_delete(self, rp, actor):
        # called before delete
        pass

    def after_delete(self, rp, actor):
        # called after commit
        pass

    @classmethod
    def parse_id(cls, rp):
        return rp.args['id']

    @classmethod
    def parse_filename(cls, rp):
        return rp.args['filename']

    @classmethod
    def create_default_with_form(cls, **kwargs):
        from .default import DEFAULT
        defo = cls._create_with_form(DEFAULT, **kwargs)
        return defo

    @classmethod
    def _create_with_form(cls, actor, **kwargs):
        rp = RequestParser()
        rp.form = kwargs.copy()
        c = cls(rp, actor)
        return c

class ContentManager:

    def __init__(self, ContentClass):
        if not issubclass(ContentClass, Content):
            raise TypeError(f'{ContentClass} should be a subclass of {Content}.')
        self.Content = ContentClass

    def query(self, rp):
        cid = self.Content.parse_id(rp)
        c = self.select_one(cid)
        return c

    # get queries
    def select(self, query):
        # specific query
        raise NotImplementedError(f'select method on {self.__class__.__name__} not implemented.')

    def select_all(self):
        # list contents
        raise NotImplementedError(f'select_all method on {self.__class__.__name__} not implemented.')

    def select_one(self, id):
        # select content by id
        raise NotImplementedError(f'select_one method on {self.__class__.__name__} not implemented.')

    # insert/update/delete queries
    def insert(self, nd):
        # insert a new content
        raise NotImplementedError(f'insert method on {self.__class__.__name__} not implemented.')

    def update(self, nd):
        # update a content
        raise NotImplementedError(f'update method on {self.__class__.__name__} not implemented.')

    def delete(self, nd):
        # delete a content
        raise NotImplementedError(f'delete method on {self.__class__.__name__} not implemented.')

    # persistence method
    def commit(self):
        # persist changes and synchronize
        raise NotImplementedError(f'commit method on {self.__class__.__name__} not implemented.')

    def rollback(self):
        # rollback changes (encountered an exception)
        raise NotImplementedError(f'rollback method on {self.__class__.__name__} not implemented.')
