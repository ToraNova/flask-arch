import jwt
import json
from flask import current_app
from werkzeug.datastructures import FileStorage

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


# using file_storage for storing profile picture (EXAMPLE OF SINGULAR FILE MANAGEMENT)
@file_storage(max_size=5*SIZE_MB, regex_whitelist=['jpe?g$', 'png$'])
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

        # initialize default profile image
        with open('wojak.jpg', 'rb') as fp:
            self.profile_img = self.store_file(FileStorage(fp))

        self.email = email

    def modify(self, rp, actor):
        #super().modify(rp, actor)

        if actor == self:
            # self update
            if len(rp.files) > 0:
                # profile picture update
                new_pi_fp = rp.files['profile_img']
                new_pi = self.store_file(new_pi_fp)
                self.remove_file(self.profile_img)
                self.profile_img = new_pi

        else:
            # other user is updating this person's profile
            # likely an admin
            self.role_id = rp.form['role_id']

    @classmethod
    def get_all_roles(cls):
        roles = MyRole.query.all()
        return roles

    @declared_attr
    def email(cls):
        return Column(String(254), unique=True, nullable=False)

    @declared_attr
    def role(cls):
        return relationship('MyRole', foreign_keys=[cls.role_id])

    @declared_attr
    def profile_img(cls):
        return Column(String(255), unique=False, nullable=True)

# allow Project contents to store files, each up to 5MB per upload
# only allow files ending in jpg, jpeg and png
# store the files separately for each content, with subdirectory created using the 'name' attribute
# EXAMPLE OF MULTIPLE FILE HANDLING
@file_storage(max_size=5*SIZE_MB, regex_whitelist=['jpe?g$', 'png$'], subdir_key='name')
class Project(SQLContent, my_declarative_base):
    __tablename__ = "project"

    def __init__(self, rp, actor):
        super().__init__(rp, actor)
        self.name = rp.form['name']

        for f in rp.files.getlist('project_files'):
            self.store_file(f)

    def view(self, rp, actor):
        if self.creator_id != actor.id:
            raise UserError(403, 'cannot view, no ownership')
        return self

    def modify(self, rp, actor):
        if self.creator_id != actor.id:
            raise UserError(403, 'cannot modify, no ownership')
        # only owners can modify
        for k, v in rp.form.items():
            if v == 'delete':
                self.remove_file(k)

        for f in rp.files.getlist('project_files'):
            self.store_file(f)

    def deinit(self, rp, actor):
        if self.creator_id != actor.id:
            raise UserError(403, 'cannot delete, no ownership')
        # only owners can delete

    def after_delete(self, rp, actor):
        # delete every file if the content is deleted
        self.remove_subdir()

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)

    @declared_attr
    def name(cls):
        return Column(String(50),unique=False,nullable=False)
