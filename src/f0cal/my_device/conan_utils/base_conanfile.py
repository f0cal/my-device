import os
import shutil
import types
import yaml
from conans import tools
from conans import ConanFile as _ConanFile

from f0cal.my_device.conan_utils.conan_data_parser import ConanDataValidator
from f0cal.my_device.conan_utils.image import Image as ConanImage


class ConanFile(_ConanFile):
    # TODO THESE ARE LIKELY TO CHANGE
    _EXPECTED_CONANDATA_KEYS = {
        'name',
        'version',
        'filename',
        'parts',
        'admin_user', # THESE TWO SHOULD EVENTAULLY BE MOVED INTO A MORE GENERAL "CONNECTION METHOD" KEY
        'admin_password'
    }
    # THIS SHOULD BE OVERWRITTEN BY SUBCLASSES
    EXTRA_CONANDATA_KEYS = set()

    settings = []
    options = []

    @property
    def filename(self):
        return self.conan_data['filename']

    @property
    def full_name(self):
        return f'{self.name}/{self.version}@{self.user}/{self.channel}'

    def _valdite_conandata(self):
        required_keys = self._EXPECTED_CONANDATA_KEYS.union(self.EXTRA_CONANDATA_KEYS)
        return ConanDataValidator.validate(self.conan_data, required_keys)

    def _init_values(self):
        self.name = self.conan_data["name"]
        self.version = str(self.conan_data['version'])

    @property
    def f0cal_yml(self):
        data = self.conan_data
        data.update({'img_file': self.filename,
                     'name': self.full_name, })
        return data

    def __init__(self, output, runner, display_name, user, channel, **kwargs):
        super().__init__(output, runner, display_name, user, channel)
        self._valdite_conandata()
        self._init_values()

    def source(self):
        raise NotImplemented

    def build(self):
        '''While this method could and perhaps should be overridden by subclasses it is important that it also writes
        the f0cal yaml to the build folder'''
        with open('f0cal.yml', 'w') as f:
            yaml.dump(self.f0cal_yml, f)

    def package(self):
        self.copy('f0cal.yml')
        self.copy(self.filename, keep_path=False)
