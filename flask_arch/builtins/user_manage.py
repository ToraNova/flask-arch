from . import privileges
from .. import base, tags, callbacks
from ..utils import ensure_type
from ..cms.base import ContentManager
from ..cms.blocks import ContentLstBlock, ContentAddBlock, ContentModBlock, ContentDelBlock
from ..user.access_policies import privilege_required

class Arch(base.Arch):

    def __init__(self, user_manager, arch_name='userman', **kwargs):
        super().__init__(arch_name, **kwargs)
        ensure_type(user_manager, ContentManager, 'user_manager')

        USERLST   = 'userlst'
        USERADD   = 'useradd'
        USERMOD   = 'usermod'
        USERDEL   = 'userdel'

        rb = ContentLstBlock(USERLST, user_manager,
                access_policy=privilege_required(privileges.USERSEL))
        self.add_route_block(rb)

        rb = ContentAddBlock(USERADD, user_manager, reroute_to=USERLST,
                access_policy=privilege_required(privileges.USERADD))
        self.add_route_block(rb)

        rb = ContentModBlock(USERMOD, user_manager, reroute_to=USERLST,
                access_policy=privilege_required(privileges.USERMOD))
        self.add_route_block(rb)

        rb = ContentDelBlock(USERDEL, user_manager, reroute_to=USERLST,
                access_policy=privilege_required(privileges.USERDEL))
        self.add_route_block(rb)

        for rb in self.route_blocks.values():
            rb.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            rb.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)
            rb.set_custom_callback(tags.INTEGRITY_ERROR, callbacks.default_int_error)
