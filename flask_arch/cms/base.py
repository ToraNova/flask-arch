# base object for the content management system
# this system also handles user

class BaseContentMixin:

    @property
    def id(self):
        if hasattr(self, 'id'):
            return self.id
        else:
            return None

    def get_id(self):
        return self.id

    @classmethod
    def create(cls, data):
        raise NotImplementedError(f'create callback on {cls.__name__} not implemented')

    def update(self,data):
        raise NotImplementedError(f'update callback on {self.__class__.__name__} not implemented')

    def delete(self, data):
        raise NotImplementedError(f'delete callback on {self.__class__.__name__} not implemented')

    @classmethod
    def populate_template_data(cls):
        raise NotImplementedError(f'populate_template_data callback on {cls.__name__} not implemented')

class BaseContentManager:

    def __init__(self, content_class):
        if not issubclass(content_class, BaseContentMixin):
            raise TypeError(f'{content_class} should be a subclass of {BaseContentMixin}')
        self.content_class = content_class

    def select_user(self, id):
        return self.select_one(id)

    # get queries
    def select(self, query):
        # specific query
        raise NotImplementedError(f'select method on {self.__class__.__name__} not implemented')

    def select_all(self):
        # list contents
        raise NotImplementedError(f'select_all method on {self.__class__.__name__} not implemented')

    def select_one(self, id):
        # select content by id
        raise NotImplementedError(f'select_one method on {self.__class__.__name__} not implemented')

    # insert/update/delete queries
    def insert(self, nd):
        # insert a new content
        raise NotImplementedError(f'insert method on {self.__class__.__name__} not implemented')

    def update(self, nd):
        # update a content
        raise NotImplementedError(f'update method on {self.__class__.__name__} not implemented')

    def delete(self, nd):
        # delete a content
        raise NotImplementedError(f'delete method on {self.__class__.__name__} not implemented')

    # persistence method
    def commit(self):
        # persist changes and synchronize
        raise NotImplementedError(f'commit method on {self.__class__.__name__} not implemented')

    def rollback(self):
        # rollback changes (encountered an exception)
        raise NotImplementedError(f'rollback method on {self.__class__.__name__} not implemented')

    def shutdown_session(self):
        raise NotImplementedError(f'shutdown_session method on {self.__class__.__name__} not implemented')

