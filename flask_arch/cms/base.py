# base object for the content management system
# this system also handles user
import datetime

class Content:
    '''ancestor of all content managed by a ContentManager'''

    def get_id(self):
        if hasattr(self, 'id'):
            return self.id
        else:
            return None

    @classmethod
    def create(cls, data):
        raise NotImplementedError(f'create callback on {cls.__name__} not implemented.')

    def update(self, data):
        raise NotImplementedError(f'update callback on {self.__class__.__name__} not implemented.')

    def delete(self, data):
        raise NotImplementedError(f'delete callback on {self.__class__.__name__} not implemented.')

    @classmethod
    def parse_id(cls, data):
        return data['id']


class ContentManager:

    def __init__(self, content_class):
        if not issubclass(content_class, Content):
            raise TypeError(f'{content_class} should be a subclass of {Content}.')
        self.content_class = content_class

    def construct(self, *args, **kwargs):
        return self.content_class(*args, **kwargs)

    def create(self, data, creator=None):
        nc = self.content_class.create(data)
        if isinstance(creator, Content):
            nc.creator_id = creator.get_id()
        nc.created_on = datetime.datetime.now()
        return nc

    def query(self, qargs):
        cid = self.content_class.parse_id(qargs)
        c = self.select_one(cid)
        return c

    def modify(self, qargs, data, modifier=None):
        ec = self.query(qargs)
        ec.update(data)
        if isinstance(modifier, Content):
            ec.modifier_id = modifier.get_id()
        ec.modified_on = datetime.datetime.now()
        return ec

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

    def parse_id(self, data):
        cid = self.content_class.parse_id(data)
        return cid
