import datetime

from . import base
from ...cms import declared_attr, Column, Integer, String, Boolean, DateTime
from ...cms.sql import Content, ContentManager, SQLDeclarativeBase

class User(base.User, Content, SQLDeclarativeBase):
    #__tablename__ = "auth_user"
    #__table_args__ = {'extend_existing': True}
    userid = 'name' # change userid to 'email', for example, specify email as user identifier

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key = True)

    @declared_attr
    def name(cls):
        return Column(String(50),unique=True,nullable=False)

    @declared_attr
    def authd(cls):
        return Column(String(160),unique=False,nullable=False)

    @declared_attr
    def is_active(cls):
        return Column(Boolean(),nullable=False) #used to disable accounts

    @declared_attr
    def created_on(cls):
        return Column(DateTime()) #date of user account creation

    @declared_attr
    def updated_on(cls):
        return Column(DateTime()) #updated time

class UserManager(ContentManager):

    def __init__(self, user_class, database_uri, orm_base=SQLDeclarativeBase):
        super().__init__(user_class, database_uri, orm_base)
        if not issubclass(user_class, User):
            raise TypeError(f'{user_class} should be a subclass of {User}.')

    def select_user(self, userid):
        return self.content_class.query.filter(
            getattr(self.content_class, self.content_class.userid) == userid
        ).first()
