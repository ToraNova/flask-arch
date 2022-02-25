
def default_success(arch, e):
    arch.flash(f'{arch.get_route_key()} successful', 'ok')

def default_user_error(arch, e):
    arch.flash(e.msg, 'err')
    return arch.render(), e.code

def default_int_error(arch, e):
    #arch.flash('already exist', 'warn')
    arch.flash(str(e), 'err')
    return arch.render(), 409

def default_login_invalid(arch, e):
    arch.flash('invalid credentials', 'err')
    return arch.render(), 401
