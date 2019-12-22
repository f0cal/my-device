import os
import types

import parse
import yaml

from conans import tools
from conans import ConanFile as _ConanFile
from conans.model.values import Values


class ConanFile(_ConanFile):
    _DEFAULT_INDEX = 'No Index Specified'
    _SPECIAL_PLACE = "img"
    _FIELD_TO_INDEX = "history"  # Note 1
    _INDEX_VAR = "F0CAL_INDEX"  # Note 2
    settings = []
    options = []
    def __init__(self, output, runner, display_name, user, channel, **kwargs):
        super().__init__(output, runner, display_name, user, channel)
        # Conan loader.py requires name and version to be mutable, even though they aren't modified.
        self.name = self.conan_data["name"]
        self.index = tools.get_env(
            self._INDEX_VAR,
            default=self.conan_data["__default__"]
        )
        self.version = self.index

    def _conan_data(self):
        _ = self.conan_data
        _.update(self.conan_data["history"][self.index])
        return types.SimpleNamespace(**_)

    @property
    def author(self):
        return self.conan_data["author"]

    @property
    def license(self):
        return self.conan_data["license"]

    @property
    def description(self):
        return self.conan_data["description"]

    @property
    def topics(self):
        return self.conan_data["topics"]

    @property
    def url(self):
        return self._conan_data().url

    @property
    def device_types(self):
        return self._conan_data().device_types

    @property
    def dtb(self):
        return self._conan_data().components['dtb']

    @property
    def initrd(self):
        return self._conan_data().components['initrd']

    @property
    def kernel(self):
        return self._conan_data().components['kernel']

    @property
    def append(self):
        return self._conan_data().components['append']

    @property
    def base(self):
        return self._conan_data().components['base']

    @property
    def pxelinux(self):
        return self._conan_data().components['pxelinux']

    def requirements(self):
        # Requiring these only to ensure they are cached locally.
        self.requires(self.dtb)
        self.requires(self.initrd)
        self.requires(self.kernel)
        self.requires(self.append)
        self.requires(self.base)
        self.requires(self.pxelinux)

    def build(self):
        component_types = {'dtb', 'initrd', 'kernel', 'append', 'base', 'pxelinux'}
        components = {component_type: getattr(self, component_type) for component_type in component_types}

        packages = dict()
        p = parse.compile("[builddirs_{packagename}]\n{path}")
        with open('conanbuildinfo.txt', 'r') as f:
            conanbuildinfo = f.read().split('\n\n')
            for entry in conanbuildinfo:
                result = p.parse(entry.strip())
                if result:
                    packages[result['packagename']] = result['path']

        with open('f0cal.yml', 'w') as f:
            component_manifest = dict()
            for component in components:
                packagename = components[component].split('/')[0]
                basepath = packages[packagename]
                component_manifest[component] = basepath
            yaml.dump({'components': component_manifest}, f)

    def package(self):
        self.copy('f0cal.yml', '.')


    def deploy(self):
        self.copy('f0cal.yml', '.')


