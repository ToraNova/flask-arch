from .base import RouteBlock
from flask_login import login_user, logout_user, LoginManager, login_required, current_user

class RenderBlock(RouteBlock):

    def view(self):
        return self.render()

class RerouteBlock(RouteBlock):

    def view(self):
        return self.reroute()
