from .. import tags, callbacks

from .base import Arch as BasicArch
from .blocks import UserlstBlock, UseraddBlock, UsermodBlock, UserdelBlock

class Arch(BasicArch):

    def __init__(self, user_manager, arch_name='auth', **kwargs):
        super().__init__(user_manager, arch_name, **kwargs)

        USERLST   = 'userlst'
        USERADD   = 'useradd'
        USERMOD   = 'usermod'
        USERDEL   = 'userdel'

        rb = UserlstBlock(USERLST, user_manager)
        self.add_route_block(rb)

        rb = UseraddBlock(USERADD, user_manager, reroute_to=USERLST)
        self.add_route_block(rb)

        rb = UsermodBlock(USERMOD, user_manager, reroute_to=USERLST)
        self.add_route_block(rb)

        rb = UserdelBlock(USERDEL, user_manager, reroute_to=USERLST)
        self.add_route_block(rb)

        for rb in self.route_blocks.values():
            rb.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            rb.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)
            rb.set_custom_callback(tags.INTEGRITY_ERROR, callbacks.default_int_error)
