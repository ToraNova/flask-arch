
def default_success(rb, e):
    rb.flash(f'{rb.keyword} successful', 'ok')

def default_user_error(rb, e):
    rb.flash(e.msg, 'err')
