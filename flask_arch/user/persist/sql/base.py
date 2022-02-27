from ...base import BaseUser
from ....cms import SQLContent
from ....cms import declared_attr, Column, Integer, String, Boolean, DateTime, ForeignKey, relationship

class User(BaseUser, SQLContent):
    __tablename__ = "auth_user"
    userid = 'name' # change userid to 'email', for example, specify email as user identifier
    #__table_args__ = {'extend_existing': True}

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
