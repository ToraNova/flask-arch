from .base import Content
from ..utils import RequestParser

class Default(Content):
    def __init__(self, rp, actor):
        pass

DEFAULT = Default(RequestParser(), None)
DEFAULT.name = 'default'
