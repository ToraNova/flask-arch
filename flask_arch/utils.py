def ensure_type(arg, typ, argn, allow_none = False):
    if not isinstance(arg, typ):
        if allow_none and arg is None:
            return
        raise TypeError(f'{argn} should be of instance {typ}, got {type(arg)}')

def ensure_callable(arg, argn, allow_none=False):
    if not callable(arg):
        if allow_none and arg is None:
            return
        raise TypeError(f'{argn} should be callable, got {type(arg)}')

def parse_boolean(reqform, attr):
    formval = reqform.get(attr)
    if isinstance(formval, bool):
        return formval
    elif isinstance(formval, str):
        return formval.lower() in ['on', '1', 'yes', 'true', 't']
    elif isinstance(formval, int):
        return formval > 0
    else:
        return False
