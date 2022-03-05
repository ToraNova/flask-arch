from flask import abort
from flask_login import current_user, login_required
from functools import wraps

from .base import Role

def privilege_required(privilege):
    def outer_dec(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                # not logged in
                abort(401)

            cu_role = current_user.get_role()
            if not isinstance(cu_role, Role):
                # role is not a base role
                abort(403)

            if not cu_role.has_privilege(privilege):
                # does not have the right privilege
                abort(403)

            # is logged in, has a role, and has the required privilege
            return fn(*args, **kwargs)
        return decorated_view
    return outer_dec

def rolename_required(rolename):
    def outer_dec(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                # not logged in
                abort(401)

            cu_role = current_user.get_role()
            if not isinstance(cu_role, Role):
                # role is not a base role
                abort(403)

            if not cu_role.name == rolename:
                # does not have the right privilege
                abort(403)

            # is logged in, has a role, and has the required privilege
            return fn(*args, **kwargs)
        return decorated_view
    return outer_dec
