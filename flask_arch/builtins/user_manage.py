from .. import base, tags, callbacks
from ..utils import ensure_type
from ..cms.base import ContentManager
from ..cms import ContentLstBlock, ContentAddBlock, ContentModBlock, ContentDelBlock, ContentFileBlock
from ..user.access_policies import privilege_required, Privileges

class Arch(base.Arch):

    def __init__(self, user_manager, arch_name='user', **kwargs):
        super().__init__(arch_name, **kwargs)
        ensure_type(user_manager, ContentManager, 'user_manager')

        GRT = 'list'

        self.privileges = Privileges(arch_name)
        self.privileges.add('view')
        self.privileges.add('add')
        self.privileges.add('mod')
        self.privileges.add('del')

        rb = ContentLstBlock(GRT, user_manager,
                access_policy=privilege_required(self.privileges.VIEW))
        self.add_route_block(rb)

        rb = ContentFileBlock('file', user_manager,
                access_policy=privilege_required(self.privileges.VIEW))
        self.add_route_block(rb)

        rb = ContentAddBlock('add', user_manager, reroute_to=GRT,
                access_policy=privilege_required(self.privileges.ADD))
        self.add_route_block(rb)

        rb = ContentModBlock('mod', user_manager, reroute_to=GRT,
                access_policy=privilege_required(self.privileges.MOD))
        self.add_route_block(rb)

        rb = ContentDelBlock('del', user_manager, reroute_to=GRT,
                access_policy=privilege_required(self.privileges.DEL))
        self.add_route_block(rb)

        for rb in self.route_blocks.values():
            rb.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            rb.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)
