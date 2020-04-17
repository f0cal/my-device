from f0cal.my_device.conan_utils.base_conanfile import ConanFile as _ConanFile
import uuid
from f0cal.services.device_farm.verbs.instance import InstanceScheduler
from f0cal.services.device_farm.instance_factories import PxeBootFactory, SelfFlashFactory
from f0cal.services.device_farm import models
from conans import ConanFile
import os


class MetaClient:
    @classmethod
    def get_instance(self, image, device_type):
        # TODO MOVE THIS ELSEWHERE
        try:
            from f0cal.services.device_farm.orchestration import get_instance
            return get_instance(image, device_type)
        except ImportError:
            pass
        raise Exception(
            "Post boot workflows only supported with local client. Please create this Image on the device farm")


class ConanFile(ConanFile):
    BASE_IMAGE = None
    # TODO GET THIS FROM CONANDATA.YML
    options = {'device_type': []}
    requires = BASE_IMAGE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = None

    def boot(self):
        self.instance = MetaClient.get_instance(self.BASE_IMAGE, self.options.device_type)
        self.instance.boot()

    def post_boot(self):
        pass

    def build(self):
        self.boot()
        self.post_boot()

    def package(self):
        self.instance.save(os.path.join(self.package_folder, f'{self.name}_{self.version}.img'))
