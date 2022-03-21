#--------------------------------------------------
# fsqlite.py (sqlalchemy ORM base)
# this file is static and should not be tampered with
# it initializes the required base models for the db engine
# introduced 8/12/2018
# migrated from rapidflask to miniflask (22 Jul 2020)
# migrated from miniflask to vials project (29 Nov 2020)
# migrated from vials project to the flask-arch project (21 Feb 2022)
# ToraNova 2022
# chia_jason96@live.com
#--------------------------------------------------

import json
import datetime
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# import copy pasta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from flask_login import current_user

from ... import base

def make_session(engine, base):
    '''create a session and bind the Base query property to it'''
    sess = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
    base.query = sess.query_property()
    return sess

class Connection:

    def __init__(self, db_uri, orm_base):
        self.uri = db_uri
        self.engine = create_engine(self.uri)
        self.orm_base = orm_base
        self.session = make_session(self.engine, self.orm_base)

    def configure_teardown(self, app):

        @app.teardown_appcontext
        def teardown(exception=None):
            self.session.remove()

class Content(base.Content):

    #_auc_name = 'flask_arch.user.persist.sql.UserManager.__init__.<locals>.AuthUser'
    _auc_name = 'AuthUser'

    def __init__(self, rp, actor):
        pass

    def as_json(self):
        return json.dumps(self.as_dict())

    def as_dict(self):
        # dump all table into a dictionary
        od = {c.name: (getattr(self, c.name)) for c in self.__table__.columns}
        for k, v in od.items():
            # convert dates to isoformat
            if isinstance(v, datetime.datetime):
                od[k] = v.isoformat()
        return od

    @declared_attr
    def created_on(cls):
        return Column(DateTime()) # date of content insertion

    @declared_attr
    def updated_on(cls):
        return Column(DateTime()) # date of content update

    @declared_attr
    def creator_id(cls):
        return Column(
            Integer,
            ForeignKey('auth_user.id', ondelete='SET NULL'),
            nullable=True
        )

    @declared_attr
    def creator(cls):
        return relationship(cls._auc_name, foreign_keys=[cls.creator_id])

    @declared_attr
    def modifier_id(cls):
        return Column(
            Integer,
            ForeignKey('auth_user.id', ondelete='SET NULL'),
            nullable=True
        )

    @declared_attr
    def modifier(cls):
        return relationship(cls._auc_name, foreign_keys=[cls.modifier_id])


class ContentManager(base.ContentManager):

    @property
    def session(self):
        return self.db_conn.session

    @property
    def database_uri(self):
        return self.db_conn.uri

    def __init__(self, ContentClass, db_conn):
        super().__init__(ContentClass)
        if not issubclass(ContentClass, Content):
            raise TypeError(f'{ContentClass} should be a subclass of {Content}.')

        if not isinstance(db_conn, Connection):
            raise TypeError(f'{db_conn} should be a subclass of {Connection}.')

        self.db_conn = db_conn
        self.tablename = self.Content.__tablename__

    # create table if not exist on dburi
    def create_table(self):
        if not self.table_exists:
            engine = create_engine(self.database_uri)
            self.Content.__table__.create(engine, checkfirst=True)
            engine.dispose() #house keeping

    # check if table exists in dburi
    @property
    def table_exists(self):
        engine = create_engine(self.database_uri)
        ins = inspect(engine)
        res = self.Content.__tablename__ in ins.get_table_names()
        engine.dispose()
        return res

    def select_all(self):
        return self.Content.query.all()

    def select_one(self, id):
        return self.Content.query.filter(self.Content.id == id).first()

    # insert/update/delete queries
    def insert(self, nd):
        # insert a new content
        self.session.add(nd)

    def update(self, nd):
        # update a content
        self.session.add(nd)

    def delete(self, nd):
        # delete a content
        self.session.delete(nd)

    # persistence method
    def commit(self):
        # persist changes and synchronize
        self.session.commit()

    def rollback(self):
        # rollback changes (encountered an exception)
        self.session.rollback()
