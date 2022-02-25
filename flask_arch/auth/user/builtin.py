# builtin user classes

import datetime
from . import base
from . import sql
from . import password

# THE ORDER MATTERS, MIXIN CLASSES MUST ALWASY BE ON THE LEFT
class BasicPasswordUser(password.UserMixin, base.User):

    def __init__(self, username, password):
        super().__init__(username, password)

class PasswordUser(password.UserMixin, sql.User):

    def __init__(self, username, password):
        super().__init__(username, password)
        self.created_on = datetime.datetime.now()
        self.updated_on = self.created_on

    def update(self, data):
        super().update(data)
        self.updated_on = datetime.datetime.now()
