'''This is conanfile which is meant to create a conan package from an image binary that is available at some url.
This is the simpliest form of the file which simply unzips the file and packages it along side the modified conandata '''
from f0cal.my_device.conan_utils.base_conanfile import ConanFile as _ConanFile
from conans import tools
import yaml
import os

class ConanFile(_ConanFile):
    EXTRA_CONANDATA_KEYS = {'url', 'download_hash'}
    def source(self):
        tools.get(self.conan_data['url'], sha256=self.conan_data['download_hash'])

