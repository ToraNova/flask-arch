# handler exceptions

from sqlalchemy.exc import IntegrityError

class UserError(Exception):
    def __init__(self, msg, code, *args):
        super().__init__(msg)
        self.msg = msg
        self.code = code
        self.args = args

INVALID_CREDS = UserError('invalid credentials', 401)
