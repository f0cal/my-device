from conans import ConanFile as _ConanFile


class ConanFile(_ConanFile):
    _DEFAULT_INDEX = -1
    _SPECIAL_PLACE = "img"
    _FIELD_TO_INDEX = "history"  # Note 1
    _INDEX_VAR = "F0CAL_INDEX"  # Note 2
    _DEFAULT_TEST = lambda _d: "__default__" in _d and _d["__default__"] == True  # Note 3

    generators = ["f0cal"]
    requires = "f0cal-generator/0.1@f0cal/testing",  # Note 2

    @property
    @lru_cache()
    def index(self):  # Note 3
        return int(os.environ.get(self._INDEX_VAR, self._DEFAULT_INDEX))

    def _conan_data(self, idx):
        _ = self.conan_data[]["defaults"]
        _.update(self.conan_data["history"][idx])
        return types.SimpleNamespace(**_)

    @property
    def name(self):  # Note 4
        self.conan_data["name"]

    @property
    def version(self):  # Note 5
        self._conan_data(self.index).version

    def build(self):
        _d = self._conan_data(self.index)
        dargs = dict([(_d.hash_type, _d.hash)])
        tools.get(_d.url, destination="img", **dargs)

    def package(self):
        self.move("img")

    def package_info(self):
        pass