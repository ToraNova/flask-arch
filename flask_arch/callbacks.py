
def default_success(rb, e):
    rb.flash(f'{rb.keyword} successful', 'ok')

def default_user_error(rb, e):
    rb.flash(e.msg, 'err')
    return rb.render(), e.code

def default_int_error(rb, e):
    #rb.flash('already exist', 'warn')
    rb.flash('integrity error', 'warn')
    return rb.render(), 409
