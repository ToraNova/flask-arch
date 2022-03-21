# handler exceptions

from sqlalchemy.exc import IntegrityError

class UserError(Exception):

    def __init__(self, code, msg, *args):
        super().__init__(msg)
        self.code = code
        self.msg = msg
        self.args = args
        self.reroute = False

INVALID_CREDS = UserError(401, 'invalid credentials')
INVALID_FNAME = UserError(400, 'invalid file name')
INVALID_FSIZE = UserError(400, 'invalid file size')
