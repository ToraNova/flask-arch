# base object for the content management system
# this system also handles user

class Content:
    '''ancestor of all content managed by a ContentManager'''

    # every content is either owned by no-one (None) or by someone
    # by default, it is owned by no-one
    owner_id = None

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(f'__init__ method on {self.__class__.__name__} not implemented.')

    def get_id(self):
        if hasattr(self, 'id'):
            return self.id
        else:
            return None

    @classmethod
    def create(cls, data, creator=None):
        raise NotImplementedError(f'create callback on {cls.__name__} not implemented.')

    def update(self,data):
        raise NotImplementedError(f'update callback on {self.__class__.__name__} not implemented.')

    def delete(self, data):
        raise NotImplementedError(f'delete callback on {self.__class__.__name__} not implemented.')

    @classmethod
    def populate_template_data(cls):
        raise NotImplementedError(f'populate_template_data callback on {cls.__name__} not implemented.')

    @property
    def __contentname__(self):
        raise ValueError(f'__contentname__ is undefined on {self.__class__.__name__}.')


class ContentManager:

    def __init__(self, content_class):
        if not issubclass(content_class, Content):
            raise TypeError(f'{content_class} should be a subclass of {Content}.')
        self.content_class = content_class

    def create(self, data):
        return self.content_class.create(data)

    # query user (specially for usermanagers only)
    def select_user(self, userid):
        raise NotImplementedError(f'select_user callback on {self.__class__.__name__} not implemented.')

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

    def shutdown_session(self):
        raise NotImplementedError(f'shutdown_session method on {self.__class__.__name__} not implemented.')
