import os
import types

import parse
import yaml

from conans import tools
from conans import ConanFile as _ConanFile


class ConanFile(_ConanFile):
    _DEFAULT_INDEX = -1
    _SPECIAL_PLACE = "img"
    _FIELD_TO_INDEX = "history"  # Note 1
    _INDEX_VAR = "F0CAL_INDEX"  # Note 2

    def __init__(self, output, runner, display_name, user, channel, **kwargs):
        super().__init__(output, runner, display_name, user, channel)
        # Conan loader.py requires name and version to be mutable, even though they aren't modified.
        self.name = self.conan_data["name"]
        self.index = int(tools.get_env(
            self._INDEX_VAR,
            default="__default__" in self.conan_data and self.conan_data["__default__"]
        ))
        self.version = self._conan_data(self.index).version

    def _conan_data(self, index):
        _ = self.conan_data
        _.update(self.conan_data["history"][index])
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
        return self._conan_data(self.index).url

    @property
    def device_types(self):
        return self._conan_data(self.index).device_types

    @property
    def dtb(self):
        return self._conan_data(self.index).components['dtb']

    @property
    def initrd(self):
        return self._conan_data(self.index).components['initrd']

    @property
    def kernel(self):
        return self._conan_data(self.index).components['kernel']

    @property
    def append(self):
        return self._conan_data(self.index).components['append']

    @property
    def base(self):
        return self._conan_data(self.index).components['base']

    @property
    def pxelinux(self):
        return self._conan_data(self.index).components['pxelinux']

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
