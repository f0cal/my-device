import yaml


class ConanData:
    def __init__(self, path):
        with open(path) as f:
            self._all_data = yaml.load(f)

    @property
    def _default_version(self):
        return self._all_data['__default__']

    @property
    def data(self):
        return self._all_data['history'][self._default_version]

    @property
    def _admin_user(self):
        return self.data['admin_user']

    @property
    def _admin_password(self):
        return self.data['admin_password']
