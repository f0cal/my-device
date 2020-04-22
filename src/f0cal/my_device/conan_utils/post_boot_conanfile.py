from f0cal.my_device.conan_utils.base_conanfile import ConanFile as _ConanFile
import os
import yaml

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


class ConanFile(_ConanFile):
    BASE_IMAGE = None
    requires = BASE_IMAGE
    def source(self):
        pass

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
        with open('f0cal.yml', 'w') as f:
            yaml.dump(self.f0cal_yml, f)

    def package(self):
        self.copy('f0cal.yml')
        self.instance.save(os.path.join(self.package_folder, self.filename))
