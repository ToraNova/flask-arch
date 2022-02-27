# exports
from .base import Content as BaseContent
from .base import ContentManager as BaseContentManager
from .volatile import ContentManager as VolatileContentManager
from .persist.sql import Content as SQLContent
from .persist.sql import ContentManager as SQLContentManager

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base

from ..utils import ensure_type
from ..blocks import RouteBlock

class ContentManageBlock(RouteBlock):

    def __init__(self, keyword, content_manager, **kwargs):
        super().__init__(keyword, **kwargs)
        ensure_type(content_manager, BaseContentManager, 'content_manager')
        self.content_manager = content_manager
