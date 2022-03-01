# basic user class to work with flask-login

from .base import BaseUser, BaseUserManager, BaseRole, no_role
from .volatile.procmem import User as ProcMemUser
from .volatile.procmem import UserManager as ProcMemUserManager

from .persist.sql import User as SQLUser
from .persist.sql import UserManager as SQLUserManager
