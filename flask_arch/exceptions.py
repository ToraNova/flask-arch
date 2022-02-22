# handler exceptions

from sqlalchemy.exc import IntegrityError

class UserError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.msg = msg
        self.code = code
