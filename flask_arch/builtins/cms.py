from ..cms import ContentLstBlock, ContentViewBlock, ContentAddBlock, ContentModBlock, ContentDelBlock, ContentFileBlock
from ..cms.base import ContentManager
from ..user.access_policies import privilege_required, Privileges
from ..utils import ensure_type
from .. import base, tags, callbacks

class Arch(base.Arch):

    def __init__(self, content_manager, arch_name, **kwargs):
        super().__init__(arch_name, **kwargs)
        ensure_type(content_manager, ContentManager, 'content_manager')

        GRT = 'list'

        self.privileges = Privileges(arch_name)
        self.privileges.add('view')
        self.privileges.add('insert')
        self.privileges.add('update')
        self.privileges.add('delete')

        rb = ContentLstBlock(GRT, content_manager,
                access_policy=privilege_required(self.privileges.VIEW))
        self.add_route_block(rb)

        rb = ContentViewBlock('view', content_manager, reroute_to=GRT,
                access_policy=privilege_required(self.privileges.VIEW))
        self.add_route_block(rb)

        rb = ContentFileBlock('file', content_manager, reroute_to=GRT,
                access_policy=privilege_required(self.privileges.VIEW))
        self.add_route_block(rb)

        rb = ContentAddBlock('insert', content_manager, reroute_to=GRT,
                access_policy=privilege_required(self.privileges.INSERT))
        self.add_route_block(rb)

        rb = ContentModBlock('update', content_manager, reroute_to=GRT,
                access_policy=privilege_required(self.privileges.UPDATE))
        self.add_route_block(rb)

        rb = ContentDelBlock('delete', content_manager, reroute_to=GRT,
                access_policy=privilege_required(self.privileges.DELETE))
        self.add_route_block(rb)

        for rb in self.route_blocks.values():
            rb.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            rb.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)
