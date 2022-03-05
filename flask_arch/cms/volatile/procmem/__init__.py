from ... import base
from .... import exceptions

class ContentManager(base.ContentManager):

    def __init__(self, content_class):
        super().__init__(content_class)
        self.data = {}

    def select_all(self):
        return self.data.values()

    def select_one(self, id):
        if id in self.data:
            return self.data[id]

    def insert(self, nd):
        if nd.get_id() in self.data:
            raise exceptions.UserError(f'{self.content_class.__name__} exists.', 409)
        self.data[nd.get_id()] = nd

    def update(self, nd):
        if nd.get_id() in self.data:
            self.data[nd.get_id()] = nd
            return self.data[nd.get_id()]

    def delete(self, nd):
        if nd.get_id() in self.data:
            del self.data[nd.get_id()]

    def commit(self):
        pass

    def rollback(self):
        pass
