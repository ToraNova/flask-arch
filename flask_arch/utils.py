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
