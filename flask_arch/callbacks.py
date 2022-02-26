
def default_success(rb, e):
    rb.flash(f'{rb.keyword} successful', 'ok')

def default_user_error(rb, e):
    rb.flash(e.msg, 'err')
    return rb.render(), e.code

def default_int_error(rb, e):
    #rb.flash('already exist', 'warn')
    rb.flash(str(e), 'err')
    return rb.render(), 409

def default_login_invalid(rb, e):
    rb.flash('invalid credentials', 'err')
    return rb.render(), 401
