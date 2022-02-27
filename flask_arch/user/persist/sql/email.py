from .base import User
from ....cms import declared_attr, Column, Integer, String, Boolean, DateTime, ForeignKey, relationship

class NameLoginUser(User):

    @declared_attr
    def email_addr(cls):
        return Column(String(254),unique=True,nullable=False)

    @declared_attr
    def email_confirmed(cls):
        return Column(Boolean(),nullable=False) # false until email is verified

class EmailLoginUser(NameLoginUser):
    userid = 'email_addr'
