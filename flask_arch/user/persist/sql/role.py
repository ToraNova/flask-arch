from .base import User as BaseUser
from ...base import Role as BaseRole
from ....cms import SQLContent
from ....cms import declared_attr, Column, Integer, String, Boolean, DateTime, ForeignKey, relationship

class User(BaseUser):

    @declared_attr
    def role_id(cls):
        return Column(
            Integer,
            ForeignKey('auth_role.id', ondelete='SET NULL'),
            nullable=True
        )

    @declared_attr
    def role(cls):
        return relationship('Role', foreign_keys=[cls.role_id])


class Role(BaseRole, SQLContent):
    __tablename__ = "auth_role"

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key = True)

    @declared_attr
    def name(cls):
        return Column(String(50),unique=True,nullable=False)

    @declared_attr
    def privileges(cls):
        return Column(String(1500),unique=True,nullable=False)
