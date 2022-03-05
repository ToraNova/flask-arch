from flask_arch.cms import SQLContent
from flask_arch.user import SQLUserWithRole, SQLRole
from flask_arch.exceptions import UserError
from flask_arch.utils import parse_boolean

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr

my_declarative_base = declarative_base()

class Role(SQLRole, my_declarative_base):
    pass

class User(SQLUserWithRole):
    userid = 'email'

    @classmethod
    def get_all_roles(cls):
        roles = Role.query.all()
        return roles

    @declared_attr
    def email(cls):
        return Column(String(254),unique=True,nullable=False)
