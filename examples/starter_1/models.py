import json
from flask_arch.cms import SQLContent
from flask_arch.user import SQLUserWithRole, SQLRole
from flask_arch.exceptions import UserError
from flask_arch.utils import parse_boolean

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr

my_declarative_base = declarative_base()

class Role(SQLRole, my_declarative_base):

    @classmethod
    def create(cls, data):

        tmp = cls(data['name'])
        po = json.loads(data['privileges'])
        for k, v in po.items():
            if v == 1:
                tmp.set_privilege(k)
        return tmp

    def update(self, data):

        po = json.loads(data['privileges'])
        for k, v in po.items():
            self.set_privilege(k, v)

    def delete(self, data):
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

class Project(SQLContent, my_declarative_base):
    __tablename__ = "project"

    def __init__(self, name):
        self.name = name

    @classmethod
    def create(cls, data):
        tmp = cls(data['name'])
        return tmp

    def update(self, data):
        self.name = data['name']

    def delete(self, data):
        pass

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)

    @declared_attr
    def name(cls):
        return Column(String(50),unique=False,nullable=False)
