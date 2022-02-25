
class LegacyRouteBlock:

    def init_bp_name(self, bp_name):
        self._bp_name = bp_name

    def _debug(self):
        print(self._bp_name)
        print(self.template)
        print(self.reroute)
        print(self.reroute_kwargs)
        print(self.custom_callbacks)
        print()

    # routeblock defines the default behavior
    def __init__(self, keyword, view_function, url_rule=None, reroute=None, reroute_external=False, **options):
        if not isinstance(keyword, str):
            raise TypeError(f'keyword must be an instance of str, not {type(keyword)}')
        if '.' in keyword:
            raise ValueError(f'keyword must not have dot (.) characters, not \'{keyword}\'')
        if not callable(view_function):
            raise ValueError(f'view_function {view_function} is not callable')
        self.keyword = keyword  # keyword of the route
        if isinstance(url_rule, str):
            self.url_rule = url_rule
        else:
            self.url_rule = f'/{self.keyword}'
        self.template = f'{keyword}.html'  # default template is always '<keyword>.html'
        self.reroute = reroute  # the reroute path
        self.reroute_external = reroute_external
        self.options = options  # options when adding url
        self.view_function = view_function  # the view function
        self.reroute_kwargs = {}
        self.custom_callbacks = {}

    def __str__(self):
        return self.keyword

    def __eq__(self, other):
        return self.keyword == other.keyword

