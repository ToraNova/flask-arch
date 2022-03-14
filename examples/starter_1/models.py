import jwt
import json
from flask import current_app

from flask_arch.cms import SQLContent, DEFAULT
from flask_arch.cms import file_storage, SIZE_MB
from flask_arch.user import SQLUserWithRole, SQLRole
from flask_arch.exceptions import UserError
from flask_arch.utils import parse_boolean

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr, declarative_base

my_declarative_base = declarative_base()

class MyRole(SQLRole, my_declarative_base):

    def set_json_privileges(self, jsonstr):
        po = json.loads(jsonstr)
        for k, v in po.items():
            self.set_privilege(k, v)

    def __init__(self, rp, actor):

        super().__init__(rp, actor)
        if rp.form.get('privileges'):
            self.set_json_privileges(rp.form['privileges'])

    def modify(self, rp, actor):
        if rp.form.get('privileges'):
            self.set_json_privileges(rp.form['privileges'])


class MyUser(SQLUserWithRole):
    userid = 'email' # indicate the user will login with 'email' as its identifier

    def __init__(self, rp, actor):
        super().__init__(rp, actor)

        if actor is None:
            # user is self-creating
            jd = jwt.decode(rp.form['jwt'], current_app.secret_key, algorithms=["HS256"])
            email = jd['email']
        elif isinstance(actor, self.__class__) or actor is DEFAULT:
            # user is created by another user
            # likely an administrator
            # or
            # the user is created as a default user
            email = rp.form['email']
            self.role_id = rp.form['role_id']

        self.email = email

    def modify(self, rp, actor):

        if actor == self:
            # self update
            if self.role and self.role.has_privilege('role.update_self'):
                # has privilege to update self
                self.role_id = rp.form['role_id']
        else:
            # other user is updating this person's profile
            # likely an admin
            self.role_id = rp.form['role_id']

        if self.role.has_privilege('role.update_self') or actor != self:
            # user has privilege to update it's own role
            # or the updator is not this user, therefore likely an admin
            self.role_id = rp.form['role_id']

    @classmethod
    def get_all_roles(cls):
        roles = MyRole.query.all()
        return roles

    @declared_attr
    def email(cls):
        return Column(String(254),unique=True,nullable=False)

    @declared_attr
    def role(cls):
        return relationship('MyRole', foreign_keys=[cls.role_id])


# allow Project contents to store files, each up to 5MB per upload
# only allow files ending in jpg, jpeg and png
# store the files separately for each content, with subdirectory created using the 'name' attribute
#@file_storage(max_size=5*SIZE_MB, regex_whitelist=['jpe?g$', 'png$'], subdir_key='name')
@file_storage(max_size=5*SIZE_MB, regex_whitelist=['jpe?g$', 'png$'])
class Project(SQLContent, my_declarative_base):
    __tablename__ = "project"

    def __init__(self, rp, actor):
        super().__init__(rp, actor)
        self.name = rp.form['name']

        if len(rp.files) > 0:
            # has some files for us to storre
            path = self.store_file(rp.files['project_img'])

    def modify(self, rp, actor):
        if self.creator_id != actor.id:
            raise UserError(403, 'cannot modify, no ownership')
        # only owners can modify
        self.name = rp.form['name']

    def deinit(self, rp, actor):
        if self.creator_id != actor.id:
            raise UserError(403, 'cannot delete, no ownership')
        # only owners can delete

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)

    @declared_attr
    def name(cls):
        return Column(String(50),unique=False,nullable=False)
