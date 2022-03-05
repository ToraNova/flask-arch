# basic user class to work with flask-login

from .base import User as BaseUser
from .base import Role as BaseRole
from .base import no_role

from .volatile.procmem import User as ProcMemUser
from .volatile.procmem import UserManager as ProcMemUserManager

from .persist.sql import User as SQLUser
from .persist.sql import UserWithRole as SQLUserWithRole
from .persist.sql import Role as SQLRole
from .persist.sql import UserManager as SQLUserManager
