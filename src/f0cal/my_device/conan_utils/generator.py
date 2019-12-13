import os
from conans.models import Generator as _Generator

class Generator(_Generator):

    _GEN_PATH_VAR = "F0CAL_OUT_PATH" # Note 1
    _DEFAULT_GEN_PATH = os.path.join(os.cwd(), "f0cal.yml") # Note 2

    @property
    def filename(self):
        return os.environ.get(self._GEN_PATH_VAR, self._DEFAULT_GEN_PATH)