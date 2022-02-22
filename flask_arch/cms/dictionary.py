from flask_arch.cms.base import BaseContentManager
from flask_arch import exceptions

class VolatileDictionary(BaseContentManager):

    def __init__(self, content_class):
        super().__init__(content_class)
        self.data = {}

    def select(self):
        return self.data.values()

    def select_one(self, id):
        if id in self.data:
            return self.data[id]

    def insert(self, nd):
        if nd.id in self.data:
            raise exceptions.UserError(409, f'{self.content_class.__name__} exists')
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

    def shutdown_session(self):
        pass
