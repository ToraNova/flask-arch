
from ... import BaseUser
from ....cms import BaseContent

class User(BaseUser, BaseContent):

    def __init__(self, rp, actor):
        super().__init__(rp, actor)
        self.id = rp.form['username']
