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

from flask_arch.cms.base import BaseContentMixin, BaseContentManager

SQLDeclarativeBase = declarative_base()

def make_session(engine, base = SQLDeclarativeBase):
    '''create a session and bind the Base query property to it'''
    sess =  scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
    base.query = sess.query_property()
    return sess

def connect(dburi, base = SQLDeclarativeBase):
    '''easy function to connect to a database, returns a session'''
    engine = create_engine(dburi)
    return make_session(engine, base)

class SQLContentMixin(BaseContentMixin):

    def as_json(self):
        return json.dumps(self.as_dict())

    def as_dict(self):
        # dump all table into a dictionary
        od = {c.name: (getattr(self, c.name)) for c in self.__table__.columns}
        for k,v in od.items():
            # convert dates to isoformat
            if isinstance(v, datetime.datetime):
                od[k] = v.isoformat()
        return od

class SQLContentManager(BaseContentManager):

    def __init__(self, content_class, database_uri, orm_base = SQLDeclarativeBase):
        super().__init__(content_class)
        if not issubclass(content_class, SQLContentMixin):
            raise TypeError(f'{content_class} should be a subclass of {SQLContentMixin}')

        self.tablename = self.content_class.__tablename__
        self.database_uri = database_uri
        self.session = connect(database_uri, orm_base)

    def select_user(self, userid):
        return self.content_class.query.filter(
            getattr(self.content_class, self.content_class.userid) == userid
        ).first()

    # create table if not exist on dburi
    def create_table(self):
        engine = create_engine(self.database_uri)
        self.content_class.__table__.create(engine, checkfirst=True)
        engine.dispose() #house keeping

    # check if table exists in dburi
    def table_exists(self):
        engine = create_engine(self.database_uri)
        ins = inspect(engine)
        res = self.content_class.__tablename__ in ins.get_table_names()
        engine.dispose()
        return res

    def select_all(self):
        return self.content_class.query.all()

    def select_one(self, id):
        return self.content_class.query.filter(self.content_class.id == id).first()

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

    def shutdown_session(self):
        self.session.remove()
