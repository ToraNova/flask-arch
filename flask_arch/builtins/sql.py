from ..user import SQLRole

from sqlalchemy.ext.declarative import declarative_base
default_base = declarative_base()

class DefaultRole(SQLRole, default_base):
    pass
