import os
import jwt
import json
import uuid
import hashlib
import datetime
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from flask_arch.cms import SQLContent, DEFAULT
from flask_arch.cms import file_storage, SIZE_MB, SIZE_KB
from flask_arch.user import SQLUserWithRole, SQLRole
from flask_arch.exceptions import UserError
from flask_arch.utils import parse_boolean

from .utils import resize_image, identicon

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr, declarative_base

my_declarative_base = declarative_base()

# TODO: remove this in production, only used for unit-testing
upload_d = 'uploads'
if os.environ.get('UPLOAD_DIR'):
    upload_d = os.environ['UPLOAD_DIR']

class MyRole(SQLRole, my_declarative_base):

    def set_json_privileges(self, jsonstr):
        po = json.loads(jsonstr)
        self.privileges = '{}'
        for k, v in po.items():
            self.set_privilege(k, v)

    def __init__(self, rp, actor):

        super().__init__(rp, actor)
        if rp.form.get('privileges'):
            self.set_json_privileges(rp.form['privileges'])

    def modify(self, rp, actor):
        if rp.form.get('privileges'):
            self.set_json_privileges(rp.form['privileges'])


@file_storage(upload_dir=upload_d, max_size=80*SIZE_KB, regex_whitelist=['jpe?g$', 'png$'], subdir_key='name')
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

        size_tuple = (30, 60, 150)
        sznm_tuple = ('s', 'm', 'l')

        for sznm, size in zip(sznm_tuple, size_tuple):
            barr = identicon.get_image(string=self.name, width=size, height=size, pad=int(size*0.1))

            ts_now = int(datetime.datetime.now().timestamp())
            store_name = secure_filename(f'{uuid.uuid4()}-{ts_now}_{sznm}.png')
            path = os.path.join(self.get_store_dir(), store_name)
            with open(path, 'wb') as f:
                f.write(barr)
            setattr(self, f'avatar_{sznm}', store_name)

        self.avatar_raw = None
        self.email = email

    def modify(self, rp, actor):
        #super().modify(rp, actor)

        if actor == self:
            # self update
            pass

        else:
            # other user is updating this person's profile
            # likely an admin
            self.role_id = rp.form['role_id']

    @classmethod
    def get_all_roles(cls):
        roles = MyRole.query.all()
        return roles

    @declared_attr
    def role(cls):
        return relationship('MyRole', foreign_keys=[cls.role_id])

    email = Column(String(254), unique=True, nullable=False)
    avatar_s = Column(String(64), unique=False, nullable=True)
    avatar_m = Column(String(64), unique=False, nullable=True)
    avatar_l = Column(String(64), unique=False, nullable=True)
    avatar_raw = Column(String(64), unique=False, nullable=True)

    def update_avatars(self, filenames):
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]

# allow Project contents to store files, each up to 5MB per upload
# only allow files ending in jpg, jpeg and png
# store the files separately for each content, with subdirectory created using the 'name' attribute
# EXAMPLE OF MULTIPLE FILE HANDLING
@file_storage(upload_dir=upload_d, max_size=5*SIZE_MB, regex_whitelist=['jpe?g$', 'png$'], subdir_key='name')
class Project(SQLContent, my_declarative_base):
    __tablename__ = "project"

    def _update_with_form(self, rp):
        self.company_full = rp.form.get('company_full')
        self.company_short = rp.form.get('company_short')
        self.customer_full = rp.form.get('customer_full')
        self.customer_short = rp.form.get('customer_short')
        if 'is_outsourced' in rp.form:
            self.outsourced_to = rp.form['outsourced_to']
        else:
            self.outsourced_to = None

        for f in rp.files.getlist('project_files'):
            self.store_file(f)

    def __init__(self, rp, actor):
        super().__init__(rp, actor)
        self.name = rp.form['name']
        self.status = 'new'

        self._update_with_form(rp)
        self.start_date = datetime.datetime.now()
        self.end_date = None

    def view(self, rp, actor):
        if self.creator_id != actor.id:
            raise UserError(403, 'cannot view, no ownership')
        # only owners can view
        return self

    def modify(self, rp, actor):
        if self.creator_id != actor.id:
            raise UserError(403, 'cannot modify, no ownership')
        # only owners can modify

        for k, v in rp.form.items():
            if v == 'delete_file':
                self.remove_file(k)

        self._update_with_form(rp)
        self.status = rp.form['status']

    def deinit(self, rp, actor):
        if self.creator_id != actor.id:
            raise UserError(403, 'cannot delete, no ownership')
        # owner can delete
        pass

    def after_delete(self, rp, actor):
        # delete every file if content is disabled
        self.remove_subdir()

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), unique=False, nullable=False)

    company_full = Column(String(60), unique=False, nullable=True)
    company_short = Column(String(20), unique=False, nullable=True)
    customer_full = Column(String(60), unique=False, nullable=True)
    customer_short = Column(String(20), unique=False, nullable=True)
    start_date = Column(DateTime, unique=False, nullable=True)
    end_date = Column(DateTime, unique=False, nullable=True)
    outsourced_to = Column(String(60),unique=False, nullable=True)
