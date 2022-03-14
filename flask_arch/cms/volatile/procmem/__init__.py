from ... import base
from .... import exceptions

class ContentManager(base.ContentManager):

    def __init__(self, Content):
        super().__init__(Content)
        self.data = {}

    def select_all(self):
        return self.data.values()

    def select_one(self, id):
        if id in self.data:
            return self.data[id]

    def insert(self, nd):
        if nd.id in self.data:
            raise exceptions.UserError(409, f'{self.Content.__name__} exists.')
        self.data[nd.id] = nd

    def update(self, nd):
        if nd.id in self.data:
            self.data[nd.id] = nd
            return self.data[nd.id]

    def delete(self, nd):
        if nd.id in self.data:
            del self.data[nd.id]

    def commit(self):
        pass

    def rollback(self):
        pass
