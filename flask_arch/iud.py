from .base import BaseArch, RouteBlock
from . import exceptions, tags
from flask import request

class IUDBlock(RouteBlock):

    def __init__(self, keyword, iud_request, iud_response, url_rule, reroute=None, reroute_external=False, **options):

        super().__init__(keyword, self.route_iud, url_rule=None, reroute=None, reroute_external=False, **options):

    def route_iud(self):
        if request.method == 'POST':
            user = None
            try:
                # iud request
                resargs = self.iud_request()
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e)
            except Exception as e:
                # client error
                self.client_error(e)

            try:
                # insert response
                return self.iud_response(*resargs)
            except exceptions.UserError as e:
                return self.custom(tags.USER_ERROR, e) # handle user error
            except exceptions.IntegrityError as e:
                self.user_manager.rollback() # rollback
                return self.custom(tags.INTEGRITY_ERROR, e) # handle integrity error
            except Exception as e:
                # server error: unexpected exception
                self.user_manager.rollback() # rollback
                self.server_error(e)

        return self.render()

class Arch(BaseArch):

    def __init__(self, ra, content_manager, keyword, iud_request, iud_response):

        RouteArch



        self.iud_request = iud_request
        self.iud_response = iud_response

        super().__init__(arch_name, [ra], templates, reroutes, reroutes_kwarg, custom_callbacks, url_prefix)

