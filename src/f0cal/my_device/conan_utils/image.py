import yaml
import json
import f0cal.core
import saltbox
import functools
import os
from conans.model.ref import ConanFileReference
from conans.client.conan_api import Conan
import subprocess
class Image:
    IMAGE_MANIFEST_FILE = 'f0cal.yml'

    def __init__(self, reference):
        self.conanfile_ref = reference

    @classmethod
    def from_reference(cls, reference_string):
        reference = ConanFileReference.loads(reference_string)
        return cls(reference)

    @property
    @functools.lru_cache()
    def info(self):
        # TODO there are probably way to get the info without installing the package however that will get us the info
        # and will not reinstall if installed already
        return self._conan_install()
    @property
    @functools.lru_cache()
    def _f0cal_img_info(self):
        package_dir = self.info['installed'][0]['packages'][0]['cpp_info']['rootpath']
        with open(os.path.join(package_dir, self.IMAGE_MANIFEST_FILE)) as f:
            img_info = yaml.load(f)
        return img_info

    @property
    @functools.lru_cache()
    def f0cal_img_info(self):
        img_info = self._f0cal_img_info
        # The f0cal.yml only states the image file relative to the package directory we update this here
        package_dir = self.info['installed'][0]['packages'][0]['cpp_info']['rootpath']
        img_info['img_file'] = os.path.join(package_dir, img_info['img_file'])
        return img_info

    def _conan_install(self):
        kwargs = {'build':['missing']}
        # options = Conan().inspect(str(self.conanfile_ref), None)['options']
        # if self.device_type is not None: # and 'device_type' in options:
        #     kwargs.update({'options': [f'device_type={self.device_type}']})
        return Conan().install_reference(self.conanfile_ref, **kwargs )

    def mount_base_image(self):
        ''' This function should take the components listed in the yaml file as well the corresponding salt recipe to
        place the neccary components in the boot directory '''
        cmd = ['salt-run', 'state.orchestrate', 'image_create']
        pillar = self.f0cal_img_info
        return self._saltbox_run(cmd, pillar=pillar, saltenv='api')


    def install(self, **kwargs):
        cmd = ["salt-call", "--local", "state.sls", "f0cal.my-device.image.install"]
        return self._saltbox_run(cmd, pillar=self.pillar_json, saltenv="f0cal-public")

    def test(self, **kwargs):
        pass

    def _import(self, **kwargs):
        pass

    @classmethod
    def _saltbox_run(cls, cmd, pillar, saltenv=None, **kwargs):
        config = saltbox.SaltBoxConfig.from_env(block=False)
        pillar_json = json.dumps(pillar)
        with saltbox.SaltBox.executor_factory(config) as api:
            api.execute(*cmd, f'saltenv={saltenv}', f'pillar={pillar_json}')

def base_image_create_args(parser):
    parser.add_argument('reference_string')

@f0cal.core.entrypoint(['my-device', 'image', 'mount'], args = base_image_create_args)
def mount_base_image(parser, core, reference_string, *args, **kwargs):
    img = Image.from_reference(reference_string)
    img.mount_base_image()
