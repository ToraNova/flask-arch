from ..cms.base import ContentManager
from ..cms.blocks import ContentLstBlock, ContentAddBlock, ContentModBlock, ContentDelBlock
from ..user.access_policies import privilege_required
from ..utils import ensure_type
from .. import base, tags, callbacks

class Arch(base.Arch):

    def __init__(self, content_manager, arch_name, **kwargs):
        super().__init__(arch_name, **kwargs)
        ensure_type(content_manager, ContentManager, 'content_manager')

        SELECT = 'select'
        INSERT = 'insert'
        UPDATE = 'update'
        DELETE = 'delete'

        rb = ContentLstBlock(SELECT, content_manager,
                access_policy=privilege_required(f'{arch_name}.{SELECT}'))
        self.add_route_block(rb)

        rb = ContentAddBlock(INSERT, content_manager, reroute_to=SELECT,
                access_policy=privilege_required(f'{arch_name}.{INSERT}'))
        self.add_route_block(rb)

        rb = ContentModBlock(UPDATE, content_manager, reroute_to=SELECT,
                access_policy=privilege_required(f'{arch_name}.{UPDATE}'))
        self.add_route_block(rb)

        rb = ContentDelBlock(DELETE, content_manager, reroute_to=SELECT,
                access_policy=privilege_required(f'{arch_name}.{DELETE}'))
        self.add_route_block(rb)

        for rb in self.route_blocks.values():
            rb.set_custom_callback(tags.SUCCESS, callbacks.default_success)
            rb.set_custom_callback(tags.USER_ERROR, callbacks.default_user_error)
            rb.set_custom_callback(tags.INTEGRITY_ERROR, callbacks.default_int_error)
