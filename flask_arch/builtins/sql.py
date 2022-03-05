from ..user import SQLRole
from ..cms import declarative_base

default_base = declarative_base()

class DefaultRole(SQLRole, default_base):
    pass
