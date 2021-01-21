# from f0cal import core
# from .conan_utils.image import Image
#
# @f0cal.CORE.entrypoint(['my-device', 'image', 'install'], args=_image_install_args)
# def _image_install(parser, core, image, device_type):
#     ref = ConanFileReference.loads(image, validate=False)
#     info = Conan().install_reference(ref, generators=["f0cal"])
#     image_obj = Image.from_yaml(info.f0cal["output_path"])
#     return image_obj.install()